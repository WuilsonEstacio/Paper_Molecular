# Paper_Molecular research workspace

This workspace contains the reproducible computational pipeline for the simplified cellular digital twin.

## Current status

- Real datasets: GSE90959 (anastasis, mouse hepatocytes) downloaded to `data/raw/` and analysed with a pre-registered test
  (`src/evaluation/gse90959_brake_driver.py`; result inconclusive). GSE86480 downloaded but excluded (no column-sample mapping).
- Mechanistic models: Legewie et al. 2006 (BioModels BIOMD0000000102/103, curated SBML) running in
  `src/simulation/` with CPNR experiments E1-E5 (`python -m simulation.run_cpnr_simulations` from `src/`).
  Mitochondrial module (Albeck 2008 BIOMD0000000220; Bagci 2006 MODEL1006230056, non-curated but verified):
  `python -m simulation.run_momp_simulations`. Results are SIMULATED; see `Documentacion/simulacion_cpnr_resultados.md`
  and the manuscript draft `Documentacion/articulo_CPNR_borrador.md`. PySB/BioNetGen/PhysiCell remain scaffolds.
- ML validation: blocked until real datasets with sufficient size are available

## Directory layout

- `data/raw` - downloaded raw public datasets
- `data/processed` - cleaned / harmonized datasets
- `models` - BioNetGen, PySB, PhysiCell scaffolds
- `src` - acquisition, preprocessing, modeling, evaluation scripts
- `results` - metrics, predictions, experiment artifacts
- `experiments` - experiment registry and run folders
- `notebooks` - exploratory analysis only
- `tests` - unit/integration checks
- `logs` - execution logs

## Reproducibility rules

- Every run must record a seed and dataset accession.
- Real data must be labeled `REAL`.
- Simulated data must be labeled `SIMULATED`.
- Derived labels must be labeled `DERIVED`.
