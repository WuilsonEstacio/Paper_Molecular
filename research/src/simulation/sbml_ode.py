"""Carga un modelo SBML (BioModels) y lo convierte en un sistema de ODEs para scipy.

Las ecuaciones de velocidad se toman literalmente de los kineticLaw del archivo SBML,
sin reescribirlas a mano, para que la simulacion sea trazable al modelo curado original.
Soporta el subconjunto de SBML que usan los modelos de este proyecto: especies en
concentracion, parametros globales, un compartimento de volumen constante, sin reglas
ni eventos (se verifica al cargar).
"""
from __future__ import annotations

from pathlib import Path

import libsbml
import numpy as np

SBML_DIR = Path(__file__).resolve().parents[2] / "models" / "sbml"


class SBMLModel:
    def __init__(self, path: Path | str):
        doc = libsbml.readSBML(str(path))
        if doc.getNumErrors(libsbml.LIBSBML_SEV_ERROR) > 0:
            raise ValueError(f"SBML con errores: {path}")
        m = doc.getModel()
        if m.getNumEvents() or m.getNumInitialAssignments():
            raise NotImplementedError("Eventos o initialAssignments no soportados")
        if any(r.getKineticLaw().getNumParameters() for r in m.getListOfReactions()):
            raise NotImplementedError("Parametros locales en kineticLaw no soportados")
        # Solo se admiten assignmentRules "observables": variables que ninguna ecuacion de velocidad usa.
        def names(node):
            out = {node.getName()} if node.isName() else set()
            for i in range(node.getNumChildren()):
                out |= names(node.getChild(i))
            return out

        kinetic_ids = set()
        for r in m.getListOfReactions():
            kinetic_ids |= names(r.getKineticLaw().getMath())
        self.observables = {}
        for rule in m.getListOfRules():
            if not rule.isAssignment() or rule.getVariable() in kinetic_ids:
                raise NotImplementedError(f"Regla no soportada: {rule.getVariable()}")
            self.observables[rule.getVariable()] = libsbml.formulaToL3String(rule.getMath())

        self.model_id = m.getId()
        self.path = Path(path)
        self.species = [s.getId() for s in m.getListOfSpecies()]
        self.species_names = {s.getId(): s.getName() for s in m.getListOfSpecies()}
        self.idx = {s: i for i, s in enumerate(self.species)}
        self.x0 = np.array([
            s.getInitialConcentration() if s.isSetInitialConcentration()
            else s.getInitialAmount() / m.getCompartment(s.getCompartment()).getSize()
            for s in m.getListOfSpecies()], dtype=float)
        if not np.all(np.isfinite(self.x0)):
            raise ValueError("Condiciones iniciales no definidas en el SBML")
        self.params = {p.getId(): p.getValue() for p in m.getListOfParameters()}
        self.params.update({c.getId(): c.getSize() for c in m.getListOfCompartments()})
        self.reaction_ids = [r.getId() for r in m.getListOfReactions()]
        self.reaction_names = {r.getId(): r.getName() for r in m.getListOfReactions()}

        self.S = np.zeros((len(self.species), m.getNumReactions()))
        exprs = []
        for j, r in enumerate(m.getListOfReactions()):
            for sr in r.getListOfReactants():
                self.S[self.idx[sr.getSpecies()], j] -= sr.getStoichiometry()
            for sr in r.getListOfProducts():
                self.S[self.idx[sr.getSpecies()], j] += sr.getStoichiometry()
            exprs.append(libsbml.formulaToL3String(r.getKineticLaw().getMath()))
        self.rate_laws = dict(zip(self.reaction_ids, exprs))
        # kineticLaw da cantidad/tiempo; la concentracion cambia como (cantidad/tiempo) / volumen del compartimento.
        vol = np.array([m.getCompartment(s.getCompartment()).getSize() for s in m.getListOfSpecies()])
        self.S = self.S / vol[:, None]

        src = ["def _rates(x, _prm):"]
        src += [f"    {s} = x[{i}]" for i, s in enumerate(self.species)]
        src += [f"    {k} = _prm[{k!r}]" for k in self.params]
        src.append("    return np.array([" + ", ".join(exprs) + "])")
        ns: dict = {"np": np}
        exec("\n".join(src), ns)  # codigo generado desde el SBML curado, no desde entrada de usuario
        self._rates = ns["_rates"]

    def rates(self, x: np.ndarray, params: dict) -> np.ndarray:
        return self._rates(x, params)

    def rhs(self, params: dict):
        S, rates = self.S, self._rates
        return lambda t, x: S @ rates(x, params)

    def observable(self, name: str, y: np.ndarray) -> np.ndarray:
        """Evalua una assignmentRule del SBML sobre una trayectoria y (especies x tiempos)."""
        env = {s: y[i] for i, s in enumerate(self.species)}
        return eval(self.observables[name], {"np": np}, env)  # expresion tomada del SBML curado


class RateRuleModel:
    """Modelo SBML expresado con rateRules + assignmentRules (p. ej. convertido desde CellML), sin <reaction>.

    Variables de estado = destinos de rateRule. Las assignmentRules se evaluan en orden topologico
    en cada paso. Interfaz compatible con SBMLModel: species, idx, x0, params, rhs(params)."""

    def __init__(self, path: Path | str):
        doc = libsbml.readSBML(str(path))
        if doc.getNumErrors(libsbml.LIBSBML_SEV_ERROR) > 0:
            raise ValueError(f"SBML con errores: {path}")
        m = doc.getModel()
        if m.getNumReactions() or m.getNumEvents() or m.getNumInitialAssignments() or m.getNumFunctionDefinitions():
            raise NotImplementedError("Solo modelos de rateRules puros")
        self.model_id = m.getId()
        self.path = Path(path)
        rate = {r.getVariable(): libsbml.formulaToL3String(r.getMath()) for r in m.getListOfRules() if r.isRate()}
        assign = {r.getVariable(): r.getMath() for r in m.getListOfRules() if r.isAssignment()}
        values = {p.getId(): p.getValue() for p in m.getListOfParameters()}
        values.update({c.getId(): c.getSize() for c in m.getListOfCompartments()})

        self.species = list(rate)
        self.idx = {s: i for i, s in enumerate(self.species)}
        self.x0 = np.array([values[s] for s in self.species], dtype=float)
        self.params = {k: v for k, v in values.items() if k not in rate and k not in assign}

        def names(node):
            out = {node.getName()} if node.isName() else set()
            for i in range(node.getNumChildren()):
                out |= names(node.getChild(i))
            return out

        order, pending = [], dict(assign)
        while pending:
            ready = [v for v, mth in pending.items() if not (names(mth) & set(pending) - {v})]
            if not ready:
                raise ValueError("Dependencias circulares en assignmentRules")
            for v in sorted(ready):
                order.append((v, libsbml.formulaToL3String(pending.pop(v)).replace("^", "**")))
        self.assignments = order

        src = ["def _f(x, _prm):"]
        src += [f"    {s} = x[{i}]" for i, s in enumerate(self.species)]
        src += [f"    {k} = _prm[{k!r}]" for k in self.params]
        src += [f"    {v} = {e}" for v, e in order]
        src.append("    return np.array([" + ", ".join(rate[s].replace("^", "**") for s in self.species) + "])")
        ns: dict = {"np": np}
        exec("\n".join(src), ns)  # codigo generado desde el SBML, no desde entrada de usuario
        self._f = ns["_f"]

    def rhs(self, params: dict):
        f = self._f
        return lambda t, x: f(x, params)


def load_legewie(variant: str = "WT") -> SBMLModel:
    """Legewie et al. 2006, PLoS Comput Biol 2:e120. WT = BIOMD0000000102, NC = BIOMD0000000103."""
    files = {"WT": "BIOMD0000000102.xml", "NC": "BIOMD0000000103.xml"}
    return SBMLModel(SBML_DIR / files[variant])


def load_albeck() -> SBMLModel:
    """Albeck et al. 2008, Mol Cell 30:11-25 (EARM). BIOMD0000000220. Moleculas/celula, segundos."""
    return SBMLModel(SBML_DIR / "BIOMD0000000220.xml")


def load_bagci() -> RateRuleModel:
    """Bagci et al. 2006, Biophys J 90:1546-59. MODEL1006230056 (NO curado; convertido desde CellML).
    microM y segundos. Verificado frente al texto del articulo en tests/test_bagci_momp.py."""
    return RateRuleModel(SBML_DIR / "MODEL1006230056.xml")
