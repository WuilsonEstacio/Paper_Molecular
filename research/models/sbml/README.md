# Modelos SBML (fuente primaria curada)

| Archivo | Modelo | Fuente | Estado |
|---|---|---|---|
| `BIOMD0000000102.xml` | Legewie2006_apoptosis_WT | BioModels, curado manualmente | Usado. Reproducido (tests en `research/tests/test_legewie_cpnr.py`) |
| `BIOMD0000000103.xml` | Legewie2006_apoptosis_NC | BioModels, curado manualmente | Usado como contraste (sin retroalimentacion de XIAP) |
| `BIOMD0000000220.xml` | Albeck2008_extrinsic_apoptosis (EARM) | BioModels, curado | Usado en M0. Reproduce el retraso variable y la MOMP rapida (tests en `test_bagci_momp.py`) |
| `MODEL1006230056.xml` | Bagci2006_ApoptoticStimuli | BioModels, **NO curado** (convertido automaticamente desde CellML) | Usado en M1-M4 tras verificarlo frente a 4 cifras del articulo |

SHA-256 (descarga del 2026-10-08):
`BIOMD0000000220.xml` `35da1450391eaa1d7329934a3b2846277e025e0dd000fc6787e2091068c0a46d` ·
`MODEL1006230056.xml` `5ee5c45bbb72c0043400b7519671aaffac79aa15cf413659c6577690bc9e90e6`

### Albeck et al. 2008 (BIOMD0000000220)

Albeck JG, Burke JM, Aldridge BB, Zhang M, Lauffenburger DA, Sorger PK. *Mol Cell* 2008;30:11-25.
doi:10.1016/j.molcel.2008.02.012, PMID 18406323. Moleculas por celula y segundos. 58 especies, 42 reacciones.
Dos compartimentos (`cell`, `mitochondrion`), ambos de volumen 1; el parametro `v = 0.07` aparece dentro
de las leyes de velocidad mitocondriales tal como lo define el SBML. Incluye assignmentRules observables
(`cPARP_frac`, etc.) que no intervienen en las ecuaciones.
**Propiedad estructural importante:** no hay sintesis ni degradacion de proteinas, el Bax activado no
vuelve a su forma inactiva y los poros (`M_hash`) son irreversibles. El modelo no tiene un estado de
supervivencia al que volver: la intervencion solo puede retrasar la muerte (experimento M0).

### Bagci et al. 2006 (MODEL1006230056)

Bagci EZ, Vodovotz Y, Billiar TR, Ermentrout GB, Bahar I. *Biophys J* 2006;90:1546-59.
doi:10.1529/biophysj.105.068122, PMID 16339882, texto completo PMC1367306. microM y segundos.
Formulado solo con rateRules y assignmentRules (31 variables de estado). Lo carga `RateRuleModel` en `sbml_ode.py`.
Incluye terminos de p53 (`p53`, `p53_thresh`) que modulan la produccion de Bax y Bcl-2. Se usan tal como vienen.

Verificacion frente al texto del articulo (`results/simulations/M1_bagci_reproduction_checks.csv`):

| Cifra del articulo | Simulado |
|---|---|
| [casp8]0 = 1e-5 microM -> supervivencia | supervivencia |
| [casp8]0 = 1e-4 microM -> apoptosis (caspasa-3 ~4.5e-3 microM "o mayor") | apoptosis, 5.65e-3 microM |
| Silla-nodo en degradacion de Bax u_Bax = 0.11 s^-1 | entre 0.108 y 0.109 (dif. 1.4 %) |
| Silla-nodo en produccion de Bax = 6.03e-6 microM/s | entre 5.9e-6 y 6.0e-6 (dif. 1.3 %) |

La diferencia de ~1.4 % es compatible con el metodo de continuacion cuasi-estacionaria usado, que
aproxima el punto silla-nodo desde el lado biestable.

**Articulo:** Legewie S, Bluthgen N, Herzel H. *Mathematical modeling identifies inhibitors of apoptosis
as mediators of positive feedback and bistability.* PLoS Comput Biol. 2006;2(9):e120.
doi:10.1371/journal.pcbi.0020120

**Descarga:** 2026-10-08 desde `https://www.ebi.ac.uk/biomodels/BIOMD0000000102` y `...103`. Licencia BioModels: CC0.

**Unidades:** concentraciones en nM, tiempo en segundos, compartimento `cytosol` = 1.

**Entrada del modelo:** `k16prod` (nM/s) es la tasa de formacion de Apaf-1 activo (apoptosoma) tras la
liberacion de citocromo c. Con el valor por defecto (0.02) Apaf-1 activo llega a 20 nM.

## Incidencias detectadas en los archivos

- `BIOMD0000000103` (NC), reaccion `v30`: su nombre dice "Apaf-1-Caspase9-Xiap-Caspase3_star degradation"
  (es decir `AC9X_C3_star`), pero la reaccion consume `AC9_starX_C3_star`. En consecuencia
  `AC9X_C3_star` no se degrada y `AC9_starX_C3_star` se degrada por dos reacciones (v30 y v32).
  No se ha corregido: el archivo se usa tal cual. El resultado cualitativo del NC (biestabilidad
  reversible) coincide con lo descrito en las notas del propio SBML.
- Varias especies del NC comparten la misma etiqueta `name` (copiada de `AC9_starX`); los `id` son correctos.

## Modelo descartado: Eissing et al. 2004

Se evaluo primero el modelo de activacion de caspasas de Eissing et al. 2004 (J Biol Chem 279:36892,
doi:10.1074/jbc.M404893200). No esta curado en BioModels y el articulo original (JBC) no pudo descargarse.
La unica tabla de parametros accesible (Waldherr et al. 2007, arXiv:q-bio/0702011, Tabla 3) **no produce
biestabilidad**: con k-12 = 540 el estado de muerte no existe. Un informe independiente (Dowdell 2025, REU
TAMU) llega a la misma conclusion y tuvo que modificar k1 y k-12 para recuperarla. Con k-12 = 40 la
biestabilidad aparece, lo que sugiere una errata de transcripcion, pero no es verificable sin el articulo
original. Por la regla del proyecto de no inventar constantes, el modelo queda **NO_VERIFICADO** y no se usa.
