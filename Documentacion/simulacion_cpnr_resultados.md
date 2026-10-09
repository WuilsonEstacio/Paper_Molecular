# Simulacion del punto de no retorno celular (CPNR) — resultados iniciales

Autor: Wuilson Estacio

Fecha: 2026-10-08 · Estado: **SIMULATED** (resultado computacional, no evidencia experimental)
Codigo: `research/src/simulation/` · Resultados: `research/results/simulations/` · Figuras: `research/figures/E*.png`
Reproducir: `cd research/src && python -m simulation.run_cpnr_simulations` (~5-7 min) · Tests: `cd research && python -m pytest tests -q`
Inventario de archivos, entorno, hashes y fuentes para verificar cada resultado: **seccion 7**.

Cada afirmacion lleva su nivel segun la regla del proyecto: **[EXP]** experimental publicado,
**[COMP]** resultado de esta simulacion, **[INF]** inferencia, **[HIP]** hipotesis a contrastar.

---

## 1. Pregunta

Si una celula recibe un estimulo apoptotico transitorio y despues se retira el estimulo
(el protocolo de anastasis de Tang et al. 2012), ¿a partir de que punto ya no puede recuperarse?
¿Cuanta caspasa-3 puede haber activado y aun asi sobrevivir? ¿Que determina la diferencia?

## 2. Modelo

**Legewie, Bluthgen & Herzel 2006**, PLoS Comput Biol 2:e120 (PMID 16978046, PMC1570177).
Via mitocondrial posterior a la liberacion de citocromo c: apoptosoma (Apaf-1) → caspasa-9 → caspasa-3,
con XIAP inhibiendo a ambas caspasas. Se usaron los archivos SBML **curados** de BioModels sin modificar
ninguna constante: BIOMD0000000102 (WT) y BIOMD0000000103 (NC, sin la retroalimentacion implicita de XIAP).
13 especies y 28 reacciones en WT. Procedencia e incidencias: `research/models/sbml/README.md`.

Se descarto Eissing et al. 2004: la tabla de parametros accesible no reproduce la biestabilidad descrita
por los propios autores y el articulo original no pudo verificarse (detalle en el mismo README).

**Validacion de la implementacion [COMP]:** se reproduce el resultado central del articulo:
el WT es biestable **irreversible** (la caspasa-3 queda activa a 48 nM aunque la entrada de apoptosoma
caiga a cero) y el NC es biestable **reversible** (vuelve a 0.03 nM). Figura `E1_histeresis_WT_vs_NC.png`.

**Protocolo in silico:** celula en reposo → pulso de formacion de apoptosoma de intensidad S durante T →
retirada del estimulo → seguimiento 28 h. *Comprometida* = caspasa-3 activa sostenida > 5 nM sin estimulo.

## 3. Resultados

### E2. El punto de no retorno existe y se cruza antes de que la caspasa-3 sea apreciable [COMP]

| Apaf-1 activo (nM) | 4 | 10 | 20 | 40 | 80 |
|---|---|---|---|---|---|
| Duracion critica T* (min) | 107 | 28 | 13.4 | 6.6 | 3.3 |
| Caspasa-3 activa al cruzar el PNR (% del total) | 1.0 | 0.5 | 0.35 | 0.26 | 0.21 |
| Pico maximo en una celula que aun se recupera (% del total) | 2.7 | 2.2 | 1.9 | 1.4 | 1.2 |

Figura `E2_punto_no_retorno_WT.png`. Por debajo de ~2.5 nM de Apaf-1 activo nunca hay compromiso.

**Consecuencia [INF]:** con los parametros publicados, el modelo predice que una celula que ha activado
mas de ~3 % de su caspasa-3 **no puede recuperarse**. Esto entra en conflicto con la observacion de
anastasis tras activacion de caspasa-3, escision de sustratos y dano de ADN **[EXP]** (Tang et al. 2012,
MBoC, doi:10.1091/mbc.e11-11-0926; OA0008). El modelo, tal como esta publicado, no explica la anastasis.

### E3/E3b. PNR y anastasis sustancial son casi mutuamente excluyentes en esta topologia [COMP]

- Sensibilidad local (cada parametro ×0.5 y ×2): ningun cambio individual produce a la vez un PNR y una
  ventana de recuperacion > 3 %. Los parametros que mas mueven el sistema son la produccion de XIAP,
  caspasa-9 y caspasa-3 y la degradacion de caspasa-3 activa; al pasar cierto umbral convierten el sistema
  en **reversible** (se recupera siempre: no hay PNR) o en **apoptosis espontanea**.
- Muestreo global (1500 juegos de parametros, todos ×/÷ hasta 3): 257 tienen PNR. En ellos la ventana
  mediana es **0.55 %** de caspasa-3, el percentil 99 es 11 % y solo **5/1500** superan el 10 %.
  En los 311 juegos reversibles la celula se recupera con una activacion mediana del **47 %**, pero alli no hay PNR.
  Figuras `E3_ventana_anastasis_XIAP_degradacion.png`, `E3b_robustez_global.png`.

**[INF]** En una red caspasa-9/caspasa-3/XIAP de este tipo, un PNR situado en el nivel de caspasas y la
anastasis tras activacion sustancial no coexisten en la misma celula. Si ambos fenomenos son reales,
el PNR fisiologico tiene que estar **aguas abajo** de la activacion de caspasa-3 (escision de sustratos
criticos, fragmentacion de ADN, permeabilizacion mitocondrial completa, perdida de membrana), y no en el
interruptor de caspasas.

### E4. En una poblacion heterogenea, la competencia para anastasis la decide el cociente XIAP:caspasa-3 [COMP]

Se simularon 600 celulas por escenario con variabilidad lognormal (CV 0.25, **supuesto**, del orden de
Sigal et al. 2006 y Spencer et al. 2009) en la produccion de caspasa-9, XIAP y caspasa-3 y en la intensidad del estimulo.
Supervivientes clasificados en *recupera tras activar caspasa-3* (pico ≥ 1 nM) o *nunca la activa*.

- Celulas normales, pulso de 90 min: 69 % comprometidas, **21 % se recuperan tras activar caspasa-3**
  (pico mediano ~40 % del total), 10 % nunca la activan.
- Pulso de 90 min, por quintil del cociente de produccion XIAP:caspasa-3:

| Quintil | Q1 (0.64) | Q2 (0.83) | Q3 (0.99) | Q4 (1.22) | Q5 (1.62) |
|---|---|---|---|---|---|
| Comprometidas | 100 % | 94 % | 82 % | 60 % | 9 % |
| Recuperadas tras activar caspasa-3 | 0 % | 6 % | 17 % | 32 % | 52 % |
| Nunca activan | 0 % | 0 % | 2 % | 8 % | 39 % |

**[INF]** La recuperacion tras una activacion fuerte ocurre en las celulas cuyo cociente XIAP:caspasa-3
las coloca en el regimen reversible. En ellas no hay PNR en el interruptor de caspasas.
La anastasis seria entonces una propiedad de **subpoblaciones**, predecible por su estado previo.

- Escenario tumoral (XIAP ×2): 92-99 % sobreviven, pero **casi todas sin activar caspasa-3**:
  es **resistencia apoptotica**, no anastasis. La fraccion tipo anastasis sube de 0 % a 9 % con pulsos largos.
  Figura `E4_poblacion_supervivencia.png`.

**[INF] para Paper 2:** "sobrevive al tratamiento" mezcla dos fenomenos con biologia y riesgo distintos.
El clasificador tiene que separar resistencia (nunca entra en C2) de anastasis tumoral (C2 → C3).

### E5. Predecir el destino desde el estado molecular al retirar el estimulo [COMP, SIMULATED]

Validacion GroupKFold dejando fuera una duracion de pulso cada vez (celulas normales, n = 4800):

| Modelo | ROC-AUC | PR-AUC | Brier |
|---|---|---|---|
| Solo caspasa-3 activa (regresion logistica) | 0.921 | 0.902 | 0.109 |
| 13 especies (regresion logistica) | 0.938 | 0.932 | 0.086 |
| 13 especies (random forest) | 0.992 | 0.993 | 0.038 |

Variables mas importantes (RF): caspasa-3 activa, caspasa-9 escindida, XIAP libre, apoptosoma-C9*.
**[INF]** La caspasa-3 activa sola (lo que mide un biosensor tipo CaspaseTracker) no basta para predecir
el destino. Hace falta el estado del inhibidor (XIAP) y de la caspasa iniciadora.
**Limite:** son datos de un modelo determinista medidos sin ruido. Estas metricas **no** son evidencia
de que la IA prediga el destino en celulas reales. Solo indican que variables habria que medir.

## 4. Predicciones contrastables [HIP]

1. **H1. El cociente XIAP:procaspasa-3 previo al estres predice la anastasis.** Celulas con cociente
   alto deberian recuperarse tras activar caspasa-3, y las de cociente bajo, morir.
   Prueba: CaspaseTracker/biosensor de caspasa + inmunofluorescencia cuantitativa de XIAP y caspasa-3
   en celula individual antes del estres. Alternativa: perturbar XIAP (siRNA / sobreexpresion) y medir
   la fraccion de anastasis tras lavado (protocolo Tang 2012/2015).
2. **H2. El PNR fisiologico esta aguas abajo de la caspasa-3.** Prueba: medir en las mismas celulas
   la escision de sustratos (PARP, ICAD) y la fragmentacion de ADN en el momento del lavado, y comprobar
   cual separa mejor recuperadas de muertas.
3. **H3. Tras el tratamiento, la supervivencia tumoral es sobre todo resistencia, y la anastasis aparece con
   pulsos largos.** Prueba: en lineas tumorales con XIAP alto, cuantificar que fraccion de supervivientes
   tiene historia de caspasa activa. Coherente con la sobreexpresion de cIAP2/NF-κB tras anastasis
   **[EXP]** en cancer colorrectal (Wang et al. 2023, Cell Death Dis, doi:10.1038/s41419-023-05916-8; OA0038).
   cIAP2 no es XIAP: la analogia es de familia (IAP), no de molecula.
4. **H4. Los supervivientes con caspasa subletal acumulan dano (estado S7).** En E2 los supervivientes
   justo bajo el PNR acumulan ~200-500 nM·min de exposicion a caspasa-3 activa. El correlato
   experimental es el dano de ADN e inestabilidad genomica por permeabilizacion mitocondrial limitada
   **[EXP]** (Ichim et al. 2015, Mol Cell, PMID 25702873; en la biblioteca, `02_Mitocondria`).

## 5. Limitaciones

- El modelo empieza **despues** de la liberacion de citocromo c. No incluye MOMP, BCL-2, ATP, ROS, Ca²⁺,
  dano de ADN ni ejecucion de muerte. "Comprometida" significa caspasa-3 sostenida, no muerte.
- Los parametros son los de Legewie 2006 (compilados de literatura in vitro, unidades nM). No estan
  ajustados a ningun tipo celular de los estudios de anastasis.
- La retirada del estimulo apaga la *formacion* de apoptosoma, pero el Apaf-1 activo ya formado decae
  con su vida media del modelo (k16 = 0.001 s⁻¹, unos 11.5 min). Un lavado experimental puede ser distinto.
- El CV 0.25 de la variabilidad celular es un supuesto, y el resultado de E4 depende de el.
- El umbral de destino (5 nM) y el de activacion (1 nM) son operativos. La separacion entre estados es de
  ~3 ordenes de magnitud (0.06 vs 48 nM), por lo que el destino es poco sensible al umbral exacto.
- Nada de esto se ha contrastado todavia con datos reales. El catalogo de datasets sigue sin descargas.

## 6. Siguientes pasos propuestos

1. Anadir un modulo **aguas arriba** (MOMP / BCL-2, p. ej. Albeck et al. 2008 EARM o Chen et al. 2007,
   solo desde SBML curado) para modelar MOMP parcial vs completa como candidato a PNR (H2).
2. Anadir un modulo **aguas abajo** minimo: escision de sustratos y dano acumulado (estado S7).
3. Buscar datos reales para contrastar H1-H3: transcriptomica de anastasis de Tang (GEO, OA0006/OA0029,
   *Sci Data* 2022), y datos de celula individual con biosensores de caspasa.
4. Cuando existan datos reales, el pipeline de E5 (GroupKFold por estudio) se reutiliza tal cual.

## 6b. Modulo mitocondrial (MOMP / BCL-2) — anadido el 2026-10-08

Codigo: `research/src/simulation/run_momp_simulations.py`. Resultados: `results/simulations/M*.csv`, `summary_momp.json`.

**Modelos.** Albeck et al. 2008 (EARM, BIOMD0000000220, curado) y Bagci et al. 2006 (MODEL1006230056,
**no curado**, verificado frente a 4 cifras de su articulo con una diferencia maxima del 1.4 %; ver
`research/models/sbml/README.md` y `M1_bagci_reproduction_checks.csv`).

**M0. Albeck: no hay estado de supervivencia [COMP].** EARM no tiene sintesis ni degradacion, el Bax
activado no se inactiva y los poros no se cierran. Inhibir por completo la caspasa-8 en el instante t
retrasa la muerte, pero no la evita una vez existe tBid. Con ligando 3000: inhibir a 1.0 h → muerte a 22.4 h;
a 1.5 h → 10.2 h; a 0.5 h (4 moleculas de tBid) → 40 % de PARP escindida a 96 h y subiendo. La aparente
supervivencia cuando la inhibicion se hace antes de 0.25 h corresponde a menos de una molecula de tBid
(artefacto del modelo continuo). **[INF]** Este modelo no puede representar la anastasis.

**M2. Bagci: la MOMP parcial es sobrevivible [COMP].** Con el bolo umbral de caspasa-8 (5.28e-5 microM),
la celula que sobrevive libera hasta el **14.5 %** de su citocromo c mitocondrial y alcanza como maximo
un **0.10 %** de la caspasa-3 del estado apoptotico. La que muere termina con el 83 % liberado.
Figura `M2_bagci_MOMP_parcial_umbral.png`.

**M3. Escenarios [COMP]** (`M3_bagci_bcl2_iap_bax_scenarios.csv`): con Bcl-2 x8 la MOMP sobrevivible sube
al 32.6 % y el umbral se multiplica por 33; con Bax x0.25 sube al 31.5 %; con IAP x8 al 24.5 %;
con Bax x8 baja al 6.7 %.

**M4. Muestreo global (1000 juegos)**: ver `summary_momp.json` → `M4` y la figura `M4_bagci_robustez_global.png`.
Los juegos cuya integracion supero el presupuesto de calculo (2e6 evaluaciones) se registran como
`integration_failed` y se informan; no se descartan en silencio.

**Comparacion con la literatura.** Concuerda cualitativamente con la *minority MOMP* (Ichim et al. 2015)
y con la liberacion subletal de citocromo c (Kalkavan et al. 2022, Cell, PMID 36055199).
**Limite:** el modelo trata las mitocondrias como un unico compartimento homogeneo y no incluye la muerte
independiente de caspasas que suele seguir a la MOMP (Tait & Green 2010).

## 6c. Primer contraste con datos reales: GSE90959 — anadido el 2026-10-08

Pre-registro escrito antes del analisis: `Documentacion/preregistro_GSE90959.md`
(SHA-256 `f8598e5145191e016b21a179fa68bb55e83aa70e71f6320a3939a695f66baa8a`, 21:53 del 2026-10-08).
Codigo: `research/src/evaluation/gse90959_brake_driver.py`. Resultados: `research/results/real_data/`.
Datos crudos: `research/data/raw/GSE90959/` (series matrix y anotacion GPL6887 de GEO).

- **Resultado: NO CONCLUYENTE** segun el criterio fijado de antemano. El indice frenos−impulsores fue
  ~0 en todos los tiempos (R0 −0.036, R3 −0.034, R6 −0.001, R24 −0.102, R48 +0.004), con p de Holm = 1.0.
- Xiap, Casp3 y Casp9 no superaron el umbral de expresion pre-registrado en la plataforma y no entraron en el indice.
- Descriptivo (no confirmatorio): en R3-R6 suben a la vez Mcl1 y Cflar (antiapoptoticos) y Bbc3/PUMA y
  Pmaip1/NOXA (proapoptoticos); Bcl2 baja. Figura `D1_GSE90959_frenos_impulsores.png`.
- **GSE86480 (HeLa, Sun et al. 2017) excluido:** las columnas de su tabla de expresion no tienen
  correspondencia publicada con las muestras (revisados GEO y SRA/ENA). Asignarlas seria inventar el diseno.
  Para usarlo habria que pedir la correspondencia a los autores o recuantificar desde las lecturas de SRA.

## 7. Trazabilidad y reproducibilidad

Esta seccion permite verificar de forma independiente cada numero de este informe.
Ejecuciones de referencia (2026-10-08): E1-E5 en `research/logs/cpnr_simulations_run.log`; M0-M4 en
`research/logs/momp_simulations_run.log` (811.5 s); GSE90959 con `python -m evaluation.gse90959_brake_driver`.
El proyecto no esta bajo control de versiones (git). Los hashes SHA-256 de abajo identifican la version
exacta de cada archivo usada en esta ejecucion. Si un archivo cambia, su hash deja de coincidir.

### 7.1 Modelos de entrada (fuente primaria)

| Archivo | Origen | SHA-256 |
|---|---|---|
| `research/models/sbml/BIOMD0000000102.xml` | https://www.ebi.ac.uk/biomodels/BIOMD0000000102 | `9be1a866da6ef6c9b31976ffa46af1500775bedcdc6d3120cfacf7cede593b79` |
| `research/models/sbml/BIOMD0000000103.xml` | https://www.ebi.ac.uk/biomodels/BIOMD0000000103 | `7c52acbbaa88cfa5cbd077559dc4bb5cef78df311bc2a35c25c0f8e48f5ba48e` |
| `research/models/sbml/BIOMD0000000220.xml` | https://www.ebi.ac.uk/biomodels/BIOMD0000000220 (Albeck 2008, curado) | `35da1450391eaa1d7329934a3b2846277e025e0dd000fc6787e2091068c0a46d` |
| `research/models/sbml/MODEL1006230056.xml` | https://www.ebi.ac.uk/biomodels/MODEL1006230056 (Bagci 2006, **no curado**) | `5ee5c45bbb72c0043400b7519671aaffac79aa15cf413659c6577690bc9e90e6` |
| `research/data/raw/GSE90959/GSE90959_series_matrix.txt.gz` | https://ftp.ncbi.nlm.nih.gov/geo/series/GSE90nnn/GSE90959/matrix/ | `9f810806add13672a813fca4f1d2a73c1b50d23e5a3ccb10b53362db80b7c718` |
| `research/data/raw/GSE90959/GPL6887.annot.gz` | https://ftp.ncbi.nlm.nih.gov/geo/platforms/GPL6nnn/GPL6887/annot/ | `b70966cc44a991c6cff3309eb2523b0a094694160698a723c98b7bba1816964f` |
| `research/data/raw/GSE86480/GSE86480_genes.rpkm.gz` (excluido, ver 6c) | https://ftp.ncbi.nlm.nih.gov/geo/series/GSE86nnn/GSE86480/suppl/ | `505ec0b5f604b66a05ce1e25c91d36cd1dc1ed188b130d0af6bd57993d8ebff2` |
| `research/data/raw/GSE86480/GSE86480_series_matrix.txt.gz` | https://ftp.ncbi.nlm.nih.gov/geo/series/GSE86nnn/GSE86480/matrix/ | `b3a01be839d691949ecdc4ebc5c3b094e2e7af17ad68deb394d01b25d1907bfc` |

**Verificacion de que no se modifico ninguna constante:** el 2026-10-08 se volvieron a descargar ambos
archivos de Legewie desde BioModels y sus SHA-256 coinciden byte a byte con las copias del proyecto. Albeck y Bagci
se descargaron una sola vez el mismo dia; sus hashes permiten comprobarlos igual. Para repetirlo:

```
curl -sL -o BIOMD0000000102.xml "https://www.ebi.ac.uk/biomodels/model/download/BIOMD0000000102?filename=BIOMD0000000102_url.xml"
curl -sL -o BIOMD0000000103.xml "https://www.ebi.ac.uk/biomodels/model/download/BIOMD0000000103?filename=BIOMD0000000103_url.xml"
sha256sum BIOMD0000000102.xml BIOMD0000000103.xml
```

El codigo lee las ecuaciones de velocidad directamente del SBML (`kineticLaw`). No hay ecuaciones
reescritas a mano. Los unicos valores que el codigo cambia son la entrada `k16prod` (el estimulo del
protocolo) y, solo en E3/E3b/E4, los factores de sensibilidad y variabilidad descritos en cada experimento.

Procedencia completa, incidencias del SBML y motivo del descarte de Eissing 2004:
`research/models/sbml/README.md`.

### 7.2 Codigo y tests

| Archivo | Funcion | SHA-256 |
|---|---|---|
| `research/src/simulation/sbml_ode.py` | Carga SBML (reacciones o rateRules) con libsbml y genera el sistema de ODEs | `6b6b3209e456cedb5a5a17c97d42bc3068f52a780fef1c2fee490f176d7818dc` |
| `research/src/simulation/cpnr_core.py` | Protocolo pulso-retirada, destino, T* (biseccion), umbrales | `19092563272b29f769ded25b2d182123bec6a884986b51b9fd41b0c5e21d9f62` |
| `research/src/simulation/run_cpnr_simulations.py` | Ejecuta E1-E5 y genera todas las tablas y figuras | `bb75fed65421b5c8395de2aef0ea62671e5815523c3eb7245bbbffeae6b82e7e` |
| `research/src/simulation/run_momp_simulations.py` | Ejecuta M0-M4 (Albeck y Bagci) | `c8a962aa05e8f79b5ab35681cc9f8d562eb9d7b411b4a5ed85dfc6ed994ed221` |
| `research/src/evaluation/gse90959_brake_driver.py` | Contraste pre-registrado con GSE90959 | `4ea5130e77ec8c163ff706720193229843c6d91b0f415924ab20ea5b92f6057a` |
| `research/tests/test_legewie_cpnr.py` | 6 tests: estructura del SBML, comportamiento publicado (WT irreversible, NC reversible), T* = 13.4 min, monotonia del destino | `bc83ac9130d10c99d226d42cc8c8f5faa41315f7ad39a00ab05158dda2902987` |
| `research/tests/test_bagci_momp.py` | 5 tests: cifras del articulo de Bagci, umbral y MOMP sobrevivible, dinamica de MOMP de Albeck | `556dfdac174deab15a8417a72f70346d1ad4f578c244ebee3aa8c195ea01f506` |
| `Documentacion/preregistro_GSE90959.md` | Pre-registro del contraste con datos reales | `f8598e5145191e016b21a179fa68bb55e83aa70e71f6320a3939a695f66baa8a` |

Resultado de los tests: **11 passed** (`python -m pytest research/tests -q`).
E1-E5 se volvieron a ejecutar con la version actual de `sbml_ode.py` (262.3 s). Todos los apartados de
`summary.json` (E1, E2, E3_baseline, E3b, E4_survival, E5) salieron identicos a la ejecucion anterior,
asi que todos los resultados proceden del mismo codigo.

Parametros fijos de la ejecucion: semilla 42 (E4) y 43 (E3b); umbral de destino 5 nM; umbral de
activacion 1 nM; horizonte tras la retirada 1e5 s; integrador LSODA con rtol 1e-7 y atol 1e-9;
tolerancia de T* de 5 s (E2) y 10 s (E3/E3b). Todos estan definidos en `cpnr_core.py` y `run_cpnr_simulations.py`.

### 7.3 Entorno

| Componente | Version |
|---|---|
| Python | 3.10.0 (Windows 11) |
| numpy | 1.26.4 |
| scipy | 1.11.4 |
| pandas | 2.0.3 |
| scikit-learn | 1.7.2 |
| matplotlib | 3.10.9 |
| python-libsbml | 5.21.2 (**instalado en esta sesion**, Python global) |
| pytest | 9.1.1 (**instalado en esta sesion**, Python global) |

Se anadieron `python-libsbml` y `matplotlib` a `research/requirements.txt`. `pytest` ya figuraba ahi pero no estaba instalado.
Con otras versiones de scipy los valores pueden variar en los ultimos decimales. Las conclusiones no dependen de eso.

### 7.4 Resultados generados (todos `data_provenance = SIMULATED`)

| Archivo | Experimento | Filas |
|---|---|---|
| `research/results/simulations/E1_hysteresis.csv` | E1 histeresis WT vs NC | 124 |
| `research/results/simulations/E2_cpnr_map_WT.csv` | E2 T* y ventana por intensidad (tabla de la seccion 3) | 11 |
| `research/results/simulations/E3_sensitivity_one_at_a_time_WT.csv` | E3 sensibilidad local ×0.5 / ×2 | 81 |
| `research/results/simulations/E3_xiap_x_c3degradation_grid_WT.csv` | E3 rejilla XIAP × degradacion de caspasa-3 | 30 |
| `research/results/simulations/E3b_global_parameter_sampling_WT.csv` | E3b muestreo global (1500 juegos) | 1500 |
| `research/results/simulations/E4_population_SIMULATED.csv` | E4 celulas individuales (2 escenarios × 600 celulas × 8 pulsos) | 9600 |
| `research/results/simulations/E4_survival_curves.csv` | E4 fracciones por destino y pulso | 16 |
| `research/results/simulations/E4_xiap_c3_ratio_quintiles_normal_90min.csv` | E4 tabla de quintiles XIAP:caspasa-3 | 5 |
| `research/results/simulations/E5_fate_prediction_SIMULATED.csv` | E5 metricas de prediccion | 6 |
| `research/results/simulations/E5_feature_importance_normal.csv` | E5 importancia de variables (normal) | 13 |
| `research/results/simulations/E5_feature_importance_tumor_XIAP_x2.csv` | E5 importancia de variables (tumoral) | 13 |
| `research/results/simulations/summary.json` | Resumen de E1-E5 y parametros de ejecucion | — |
| `research/results/simulations/M0_albeck_caspase8_inhibitor_rescue.csv` | M0 rescate por inhibicion de caspasa-8 (Albeck) | 18 |
| `research/results/simulations/M1_bagci_reproduction_checks.csv` | M1 verificacion de Bagci frente al articulo | 4 |
| `research/results/simulations/M2_bagci_threshold_default.csv` | M2 umbral y MOMP sobrevivible (parametros publicados) | 1 |
| `research/results/simulations/M3_bagci_bcl2_iap_bax_scenarios.csv` | M3 escenarios Bcl-2 / IAP / Bax | 18 |
| `research/results/simulations/M4_bagci_global_sampling.csv` | M4 muestreo global (1000 juegos) | 1000 |
| `research/results/simulations/summary_momp.json` | Resumen de M0-M4 | — |
| `research/results/real_data/GSE90959_brake_driver_index.csv` | Indice pre-registrado por tiempo (**REAL/DERIVED**) | 5 |
| `research/results/real_data/GSE90959_model_genes_per_timepoint.csv` | log2FC, t, p y q por gen y tiempo (**REAL/DERIVED**) | 80 |
| `research/results/real_data/GSE90959_gene_set_status.csv` | Presencia y expresion de los genes de los conjuntos | 20 |
| `research/results/real_data/GSE90959_summary.json` | Resumen y veredicto | — |

| Figura | Experimento |
|---|---|
| `research/figures/E1_histeresis_WT_vs_NC.png` | E1 |
| `research/figures/E2_punto_no_retorno_WT.png` | E2 |
| `research/figures/E3_ventana_anastasis_XIAP_degradacion.png` | E3 |
| `research/figures/E3b_robustez_global.png` | E3b |
| `research/figures/E4_poblacion_supervivencia.png` | E4 |
| `research/figures/M2_bagci_MOMP_parcial_umbral.png` | M2 |
| `research/figures/M4_bagci_robustez_global.png` | M4 |
| `research/figures/D1_GSE90959_frenos_impulsores.png` | GSE90959 |

**Donde verificar cada cifra del informe:**

| Cifra en el informe | Archivo y columna |
|---|---|
| WT 48 nM / NC 0.03 nM tras retirar el estimulo | `summary.json` → `E1` |
| T*, % de caspasa-3 al cruzar el PNR, pico en supervivientes | `E2_cpnr_map_WT.csv` → `T_star_min`, `survivor_c3_at_withdrawal_nM`, `survivor_c3_peak_pct_total` |
| 257 PNR, mediana 0.55 %, p99 11 %, 5/1500 > 10 %, mediana reversible 47 % | `summary.json` → `E3b` |
| 69 % / 21 % / 10 % con pulso de 90 min | `E4_survival_curves.csv`, fila `normal`, `pulse_min = 90` |
| Tabla de quintiles | `E4_xiap_c3_ratio_quintiles_normal_90min.csv` |
| ROC-AUC 0.921 / 0.938 / 0.992 | `E5_fate_prediction_SIMULATED.csv` |
| 200-500 nM·min de exposicion | `E2_cpnr_map_WT.csv` → `survivor_exposure_nM_min` |
| Albeck: muerte retrasada (22.4 h, 10.2 h...) | `M0_albeck_caspase8_inhibitor_rescue.csv` |
| Bagci: umbral 5.28e-5, MOMP sobrevivible 14.5 %, caspasa-3 0.10 % | `M2_bagci_threshold_default.csv` |
| Escenarios Bcl-2 x8 (32.6 %), Bax x0.25 (31.5 %), IAP x8 (24.5 %) | `M3_bagci_bcl2_iap_bax_scenarios.csv` |
| Bagci global: 546 con umbral, mediana 1.5 %, p90 28.7 %, 16 juegos > 10 % de caspasa-3 | `summary_momp.json` → `M4` y `M4_bagci_global_sampling.csv` |
| Indice GSE90959 y veredicto NO_CONCLUYENTE | `GSE90959_brake_driver_index.csv`, `GSE90959_summary.json` |

### 7.5 Otros documentos modificados en esta sesion

| Archivo | Cambio |
|---|---|
| `research/models/sbml/README.md` | Nuevo: procedencia, unidades, incidencias del SBML NC y descarte de Eissing 2004 |
| `research/requirements.txt` | Anadidos `python-libsbml` y `matplotlib` |
| `research/README.md` | Estado de "Mechanistic models" actualizado |
| `Documentacion/DIGITAL_TWIN_README.md` | Estado de "Modelos mecanisticos" actualizado |
| `research/results/experiment_registry.csv` | Filas `SIM_E1_E5_legewie2006`, `SIM_M0_M4_momp` y `REAL_GSE90959_brake_driver` |
| `research/models/sbml/` | Anadidos BIOMD0000000220 (Albeck) y MODEL1006230056 (Bagci); README ampliado |
| `research/data/raw/GSE90959/`, `research/data/raw/GSE86480/` | Datos descargados de GEO (sin modificar) |
| `Documentacion/preregistro_GSE90959.md` | Nuevo: pre-registro del contraste con datos reales |
| `Documentacion/articulo_CPNR_borrador.md` | Nuevo: borrador del articulo |

No se borro ni sobrescribio ningun archivo previo del proyecto. Los placeholders de PySB/BioNetGen/PhysiCell
siguen como estaban.

### 7.6 Fuentes consultadas

| Fuente | Uso |
|---|---|
| Legewie S, Bluthgen N, Herzel H. PLoS Comput Biol 2006;2(9):e120. PMID 16978046, PMC1570177, doi:10.1371/journal.pcbi.0020120 | Modelo usado |
| Eissing T et al. J Biol Chem 2004;279:36892. PMID 15208304, doi:10.1074/jbc.M404893200 | Modelo evaluado y descartado (articulo no descargable: JBC bloquea la descarga automatizada) |
| Waldherr S et al. 2007, arXiv:q-bio/0702011 (https://arxiv.org/abs/q-bio/0702011), Tablas 2-3 | Unica tabla de parametros de Eissing accesible; no reproduce la biestabilidad |
| Dowdell 2025, informe REU, Texas A&M (https://artsci.tamu.edu/mathematics/_files/_docs/reu/results/2025/dowdell-report.pdf) | Confirmacion independiente de que la tabla de Waldherr es monoestable |
| Tang HL et al. Mol Biol Cell 2012. doi:10.1091/mbc.e11-11-0926, PMID 22535522 (OA0008) | Protocolo de anastasis y evidencia experimental contrastada |
| Ichim G et al. Mol Cell 2015. PMID 25702873 (biblioteca: `02_Mitocondria`) | Correlato experimental de H4 |
| Wang R et al. Cell Death Dis 2023. doi:10.1038/s41419-023-05916-8, PMID 37391410 (OA0038) | Correlato experimental de H3 |
| Sigal A et al. Nature 2006;444:643; Spencer SL et al. Nature 2009;459:428 | Orden de magnitud de la variabilidad celula-a-celula (supuesto CV 0.25) |
| Albeck JG et al. Mol Cell 2008;30:11-25. PMID 18406323, doi:10.1016/j.molcel.2008.02.012 | Modelo M0 |
| Bagci EZ et al. Biophys J 2006;90:1546-59. PMID 16339882, PMC1367306, doi:10.1529/biophysj.105.068122 | Modelo M1-M4; cifras de verificacion tomadas del texto completo en PMC |
| Tang HM et al. Sci Data 2022;9:418. PMID 35851273, doi:10.1038/s41597-022-01470-8 | Datos GSE90959 |
| Sun G et al. J Cell Biol 2017;216:3355-68. PMID 28768686, doi:10.1083/jcb.201706134 | Datos GSE86480 (excluidos) |
| Kalkavan H et al. Cell 2022;185:3356. PMID 36055199; Tait SWG, Green DR. Nat Rev Mol Cell Biol 2010;11:621. PMID 20683470 | Discusion del modulo MOMP |
| Lista completa de referencias del articulo (24), verificadas en Europe PMC, Crossref o el texto original | `Documentacion/articulo_CPNR_borrador.md` |
