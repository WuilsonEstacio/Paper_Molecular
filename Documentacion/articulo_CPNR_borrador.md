# ¿Dónde está el punto de no retorno celular? Análisis computacional de la reversibilidad de la apoptosis y la anastasis en modelos mecanísticos publicados

**Where is the cellular point of no return? A computational analysis of apoptosis reversibility and anastasis in published mechanistic models**

Autor: Wuilson Estacio

Borrador v0.1 · 2026-10-08 · Estado: manuscrito en preparación, no revisado por pares.
Todos los resultados numéricos proceden de simulaciones (`data_provenance = SIMULATED`), salvo la sección 3.7 (datos públicos reales, GSE90959).
Cada cifra puede rastrearse a un archivo del repositorio (Material suplementario S1).

---

## Resumen

**Antecedentes.** La anastasis, es decir, la recuperación de células que han activado las caspasas efectoras, cuestiona que la activación de caspasa-3 o la permeabilización de la membrana mitocondrial externa (MOMP) marquen un punto de no retorno. No está claro dónde se sitúa ese punto ni de qué depende.

**Métodos.** Simulamos un protocolo de estímulo transitorio y retirada, análogo al de los experimentos de anastasis, en tres modelos mecanísticos publicados. Dos son curados en BioModels: Legewie et al. 2006 (caspasa-9/caspasa-3/XIAP) y Albeck et al. 2008 (vía extrínseca completa con MOMP). El tercero no está curado, pero lo verificamos frente a cuatro cifras de su artículo: Bagci et al. 2006 (Bax/Bcl-2, poros mitocondriales y recambio proteico). No modificamos ninguna constante publicada. Analizamos la sensibilidad local y global de los parámetros (1500 y 1000 juegos), la variabilidad célula a célula y la capacidad predictiva del estado molecular en el momento de la retirada. Contrastamos además una hipótesis derivada de las simulaciones, pre-registrada, con un conjunto de datos transcriptómicos públicos de anastasis (GSE90959).

**Resultados.** En el modelo de Legewie, el punto de no retorno se cruza cuando solo un 0.2–1.0 % de la caspasa-3 está activa, y ninguna célula que se recupera supera el 2.7 %. En el muestreo global, un punto de no retorno y la recuperación tras activación sustancial de caspasa-3 rara vez coexisten: solo 5 de los 257 juegos con punto de no retorno (1.9 %) superan una ventana del 10 %. En una población heterogénea, la recuperación tras activación fuerte de caspasa-3 aparece en las células con un cociente de producción XIAP:caspasa-3 alto: 52 % en el quintil superior frente a 0 % en el inferior. Duplicar XIAP produce sobre todo resistencia (las células no llegan a activar caspasa-3), no anastasis. El modelo de Albeck carece de procesos de reversión: inhibir la caspasa-8 retrasa la muerte pero no la evita una vez existe tBid. En el modelo de Bagci, que sí tiene recambio proteico, una célula sobrevive tras liberar hasta el 14.5 % de su citocromo c, y hasta el 33 % si se multiplica por 8 la producción de Bcl-2. En el muestreo global (546 juegos con umbral), la MOMP sobrevivible tuvo una mediana del 1.5 % y un percentil 90 del 28.7 %, mientras que la supervivencia con más del 10 % de la caspasa-3 del estado apoptótico se dio en el 2.9 % de los juegos. El punto de no retorno precede, por tanto, a la MOMP completa. En los datos reales no encontramos el desplazamiento transcripcional hacia los inhibidores que planteaba la hipótesis (resultado no concluyente). Además, tres genes clave (Xiap, Casp3, Casp9) no superaron el umbral de expresión de la plataforma.

**Conclusiones.** En los tres modelos, el punto de no retorno se sitúa antes de la activación masiva de caspasa-3 y antes de la MOMP completa. Su posición depende del equilibrio entre inhibidores (XIAP, Bcl-2) y efectores (caspasas, Bax). La anastasis tras activación sustancial de caspasas, frecuente en los experimentos, solo aparece en menos del 3 % de los parámetros de estos modelos. Requiere heterogeneidad celular en ese equilibrio o mecanismos de reversión que los modelos no incluyen. Proponemos predicciones contrastables a nivel de célula individual.

**Palabras clave:** anastasis; apoptosis; punto de no retorno; MOMP; XIAP; Bcl-2; biestabilidad; modelos mecanísticos; SBML.

### Abstract

Anastasis, the recovery of cells after effector-caspase activation, challenges the view that caspase-3 activation or mitochondrial outer membrane permeabilization (MOMP) mark a point of no return (PNR). We simulated a transient-stimulus/withdrawal protocol in three published mechanistic models without altering any published constant: Legewie et al. 2006 and Albeck et al. 2008 (curated, BioModels) and Bagci et al. 2006 (non-curated, verified against four figures of the original article). In the Legewie model the PNR is crossed with only 0.2–1.0 % of caspase-3 active, and global sampling showed that a PNR and recovery after substantial caspase-3 activation rarely coexist (5 of 257 parameter sets with a PNR, 1.9 %, had a recovery window above 10 %). In heterogeneous populations, recovery after strong activation was confined to cells with a high XIAP:caspase-3 production ratio. The Albeck model lacks reversal processes, so caspase-8 inhibition delayed but did not prevent death. In the Bagci model, which includes protein turnover, cells survived release of up to 14.5 % of mitochondrial cytochrome c (33 % with 8-fold Bcl-2 production; median 1.5 % and 90th percentile 28.7 % across 546 sampled parameter sets with a threshold), placing the PNR before complete MOMP; survival with more than 10 % of apoptotic-state caspase-3 occurred in 2.9 % of sets. A pre-registered test of a simulation-derived hypothesis in public anastasis transcriptomes (GSE90959) was inconclusive. Across models, the PNR precedes massive caspase-3 activation and complete MOMP and is set by the inhibitor:effector balance; experimentally observed anastasis after substantial caspase activation requires cell-to-cell heterogeneity or downstream reversal mechanisms absent from current models.

---

## 1. Introducción

La apoptosis se ha descrito tradicionalmente como un programa irreversible. Una vez liberado el citocromo c y activadas las caspasas efectoras, la célula quedaría comprometida a morir. Varios trabajos experimentales contradicen esa idea. Tang et al. (2012) mostraron que células primarias y líneas celulares expuestas a un inductor de apoptosis presentaban fragmentación mitocondrial, activación de caspasa-3 y daño en el ADN, y que la gran mayoría se recuperaba al retirar el inductor. Algunas de ellas adquirían cambios genéticos permanentes y transformación oncogénica [1]. El fenómeno se denominó anastasis [2]. Biosensores de actividad caspásica pasada han documentado células que sobreviven a la activación de caspasa-3 in vivo, en *Drosophila* [3, 4]. A nivel transcriptómico, la anastasis se ha descrito como un programa activo en dos etapas [5], y existen series temporales públicas de su transcriptoma [6]. La MOMP se ha considerado a menudo el punto de no retorno de la apoptosis, porque incluso sin actividad caspásica las células suelen morir tras ella por disfunción mitocondrial progresiva [7, 8]. Sin embargo, la permeabilización limitada de la membrana mitocondrial externa (*minority MOMP*) permite la supervivencia con activación caspásica subletal, daño en el ADN e inestabilidad genómica [7], y la liberación subletal de citocromo c genera células persistentes tolerantes a fármacos [9]. En cáncer colorrectal, la anastasis se ha asociado a metástasis y quimiorresistencia, con aumento de cIAP2/NF-κB [10].

Estas observaciones plantean una pregunta cuantitativa: **¿dónde está el punto de no retorno (PNR) de la apoptosis y qué lo determina?** Los modelos matemáticos de la red apoptótica describen la activación de caspasas como un interruptor biestable. En el modelo de Legewie et al. (2006), la retroalimentación implícita mediada por XIAP convierte la biestabilidad en irreversible [11]. En el modelo de Albeck et al. (2008), la MOMP actúa como un interruptor de acción rápida tras un retraso variable [12, 13]. En el modelo de Bagci et al. (2006), la cooperatividad del apoptosoma y el equilibrio Bax/Bcl-2 determinan la biestabilidad [14]. Si un modelo es biestable, el PNR tiene una definición precisa: la frontera (separatriz) entre las cuencas de atracción del estado vivo y del estado apoptótico.

En este trabajo usamos esa definición para preguntar, en modelos publicados y sin modificar sus constantes:

1. cuánta caspasa-3 activa es compatible con la recuperación tras retirar el estímulo;
2. si la MOMP completa es el punto de no retorno;
3. qué parámetros desplazan ese punto, con especial atención a los inhibidores sobreexpresados en tumores (XIAP, Bcl-2);
4. si una hipótesis derivada de las simulaciones se observa en datos transcriptómicos públicos de anastasis.

## 2. Métodos

### 2.1 Modelos y procedencia

| Modelo | Fuente | Estado | Contenido | Unidades |
|---|---|---|---|---|
| Legewie et al. 2006 [11], WT y NC | BioModels BIOMD0000000102 / 103 | Curado | Apaf-1 (apoptosoma), caspasa-9, caspasa-3, XIAP, con síntesis y degradación | nM, s |
| Albeck et al. 2008 (EARM) [12, 13] | BioModels BIOMD0000000220 | Curado | Ligando-receptor, caspasa-8, Bid/tBid, Bax, Bcl-2, poros, citocromo c, Smac, apoptosoma, caspasas-3/6/9, XIAP, PARP; sin recambio proteico | moléculas/célula, s |
| Bagci et al. 2006 [14] | BioModels MODEL1006230056 | **No curado** (convertido desde CellML) | Caspasa-8, Bid, Bax, Bcl-2, dímeros de Bax, citocromo c, apoptosoma cooperativo, caspasas-9/3, IAP, con síntesis y degradación | µM, s |

Los archivos SBML [15] se descargaron de BioModels [16] el 2026-10-08 y se usan sin modificar. Sus SHA-256 coinciden con una segunda descarga independiente (Material S1). Las ecuaciones de velocidad se leen directamente del SBML con libsbml: no hay ecuaciones transcritas a mano. Las ODE se integran con LSODA (SciPy [17]).

**Verificación de la implementación.**
- *Legewie, WT y NC:* reproducimos el resultado central del artículo. Tras retirar por completo la entrada de apoptosoma, el WT mantiene 48.1 nM de caspasa-3 activa (biestabilidad irreversible) y el NC vuelve a 0.03 nM (biestabilidad reversible) (Fig. 1).
- *Albeck:* reproducimos el retraso largo y dependiente de la dosis, seguido de una MOMP rápida. Con el ligando por defecto, el citocromo c pasa del 10 % al 90 % liberado entre 3.18 h y 3.33 h, y la PARP está escindida al 50 % a las 3.65 h.
- *Bagci:* al no estar curado, lo verificamos frente a cifras de su artículo (texto completo en PMC1367306). Un bolo inicial de caspasa-8 de 10⁻⁵ µM lleva a supervivencia y uno de 10⁻⁴ µM a apoptosis, como en el artículo. El estado apoptótico desaparece con una tasa de degradación de Bax entre 0.108 y 0.109 s⁻¹ (artículo: 0.11 s⁻¹; diferencia 1.4 %) y con una producción de Bax entre 5.9 y 6.0 × 10⁻⁶ µM/s (artículo: 6.03 × 10⁻⁶; diferencia 1.3 %).

**Modelo descartado.** El modelo de Eissing et al. (2004) [18] no está curado. La única tabla de parámetros accesible (Waldherr et al. 2007 [19]) no produce la biestabilidad que describen sus autores, y no pudimos acceder al artículo original para resolver la discrepancia. No lo usamos.

### 2.2 Protocolo de estímulo transitorio y retirada

**Legewie.** Desde el estado estacionario sin estímulo, la tasa de formación de apoptosoma activo (`k16prod`, nM/s) se fija en S durante T segundos y después en 0. El seguimiento posterior dura 10⁵ s (~28 h). La célula se clasifica como *comprometida* si la caspasa-3 activa libre se mantiene por encima de 5 nM sin estímulo (estado de muerte ≈ 48 nM; estado vivo ≈ 0.06 nM). La duración crítica T\* se obtiene por bisección; comprobamos numéricamente que el destino es monótono en T. La *ventana de anastasis* es la caspasa-3 activa máxima, en % del total, alcanzada por una célula que aún se recupera.

**Albeck.** Como el receptor activado no se inactiva, retirar el ligando no detiene la señal. Usamos como intervención la inhibición completa de la actividad catalítica de la caspasa-8 en el instante t (análoga a un inhibidor tipo z-IETD), y seguimos la célula hasta 96 h. Muerte = PARP escindida ≥ 50 %.

**Bagci.** Usamos el estímulo del propio artículo: un bolo inicial de caspasa-8 activa, que decae con su tasa de degradación. Muerte = caspasa-3 activa estacionaria > 10⁻⁴ µM (estado apoptótico ≈ 5.7 × 10⁻³ µM), evaluada a 10⁶ s porque las trayectorias próximas al umbral tardan más de 80 h en decidirse. Para el bolo umbral (bisección logarítmica, precisión relativa 10⁻⁷) medimos la liberación máxima de citocromo c mitocondrial y la caspasa-3 máxima de la trayectoria que aún sobrevive.

### 2.3 Sensibilidad, heterogeneidad y predicción

- **Sensibilidad local:** cada parámetro × 0.5 y × 2 (Legewie).
- **Sensibilidad global:** factores log-uniformes en [1/3, 3] sobre todos los parámetros cinéticos; 1500 juegos en Legewie (semilla 43) y 1000 en Bagci (semilla 44, excluyendo el exponente de cooperatividad y los términos de p53). Cada juego se clasifica en un régimen: PNR alcanzable, reversible, sin activación, apoptosis espontánea, o irreversible no alcanzado.
- **Escenarios tumorales:** producción de XIAP × 0.5–4 y degradación de caspasa-3 activa × 1–16 (Legewie); producción de Bcl-2, IAP y Bax × 0.25–8 (Bagci).
- **Variabilidad célula a célula (Legewie):** 600 células por escenario, con producción de caspasa-9, XIAP y caspasa-3 y la intensidad del estímulo lognormales (CV = 0.25, semilla 42). El CV es un supuesto del orden de las variabilidades proteicas medidas en células humanas [20, 21]; no se ajustó a ningún tipo celular. Escenarios: normal y XIAP × 2. Ocho duraciones de pulso (5–90 min). Clases de destino: comprometida; *recuperada tras activar caspasa-3* (pico ≥ 1 nM, 0.5 % del total); *nunca activada*.
- **Predicción del destino:** a partir de las 13 especies en el momento de la retirada (log10), con regresión logística y bosque aleatorio. Validación agrupada dejando fuera una duración de pulso cada vez (GroupKFold). Métricas: ROC-AUC, PR-AUC y Brier.

### 2.4 Contraste con datos reales (pre-registrado)

Antes de calcular ningún resultado registramos la hipótesis, los conjuntos de genes y la prueba (archivo `preregistro_GSE90959.md`, SHA-256 `f8598e51…`, 2026-10-08 21:53).

- **Datos:** GSE90959 [6, 22], hepatocitos primarios de ratón tratados con etanol al 4.5 % durante 5 h, lavados y recuperados 0, 3, 6, 24 y 48 h; n = 3 por grupo; Illumina MouseWG-6 v2.0, log2 normalizado por los autores.
- **Hipótesis:** durante la recuperación, el índice I(t) = media log2FC(frenos) − media log2FC(impulsores) es mayor que 0.
  - Frenos: Xiap, Bcl2, Cflar, Bfar.
  - Impulsores: Casp3, Casp9, Apaf1, Casp8, Bid, Bax, Cycs, Diablo, Casp6.
  - Solo se incluyeron especies presentes en los modelos.
- **Prueba:** nulo empírico con 10 000 pares de conjuntos aleatorios del mismo tamaño y corrección de Holm [23] sobre los cuatro tiempos de recuperación. Por gen: t de Welch y FDR de Benjamini-Hochberg [24].
- **Dataset excluido:** GSE86480 (HeLa, RNA-seq [5]). Su tabla de expresión usa identificadores de columna sin correspondencia publicada con las muestras.

## 3. Resultados

### 3.1 El interruptor de caspasas del modelo de Legewie es irreversible y su punto de no retorno se cruza con muy poca caspasa-3 activa

Con el estímulo nominal (Apaf-1 activo de 20 nM), la duración crítica fue T\* = 13.4 min. Una célula expuesta 1 min menos vuelve al estado basal; una expuesta 1 min más queda en el estado de muerte autosostenido (Fig. 2, izquierda). T\* disminuye con la intensidad del estímulo (Tabla 1; Fig. 2, derecha). Por debajo de ~2.5 nM de Apaf-1 activo no hay compromiso en 6 h.

**Tabla 1.** Frontera del punto de no retorno en el modelo de Legewie (WT).

| Apaf-1 activo (nM) | 4 | 10 | 20 | 40 | 80 |
|---|---|---|---|---|---|
| T\* (min) | 107.3 | 27.8 | 13.4 | 6.6 | 3.3 |
| Caspasa-3 activa al cruzar el PNR (% del total) | 1.04 | 0.52 | 0.35 | 0.26 | 0.21 |
| Pico máximo en una célula que se recupera (% del total) | 2.71 | 2.18 | 1.86 | 1.39 | 1.18 |
| Exposición acumulada a caspasa-3 en esa célula (nM·min) | 492 | 335 | 279 | 218 | 195 |

Dicho de otro modo, con los parámetros publicados el modelo predice que una célula que ha activado más del ~3 % de su caspasa-3 no puede recuperarse.

### 3.2 Un punto de no retorno y la recuperación tras activación sustancial rara vez coexisten

- **Sensibilidad local:** de 80 cambios individuales de parámetro (× 0.5 o × 2), 72 mantuvieron un PNR alcanzable, con una ventana máxima del 2.7 % (k15 × 0.5). Los demás llevaron a régimen reversible (6), sin activación (1) o apoptosis espontánea (2).
- **Rejilla XIAP × degradación de caspasa-3 activa (Fig. 3):** aumentar la producción de XIAP × 1.5, o la degradación de caspasa-3 activa × 4, convierte el sistema en reversible: la célula se recupera de activaciones del 16–65 %, pero ya no existe PNR. Con XIAP × 2 o más, el estímulo nominal no llega a activar caspasa-3. Con XIAP × 0.5 y degradación × 1–4, la célula entra en apoptosis espontánea.
- **Muestreo global (1500 juegos, Fig. 4):**

| Régimen | Juegos |
|---|---|
| PNR alcanzable | 257 |
| Reversible con activación | 311 |
| Sin activación | 423 |
| Apoptosis espontánea | 505 |
| Irreversible no alcanzado | 4 |

En los juegos con PNR, la ventana de anastasis tuvo una mediana del 0.55 %, un percentil 90 del 3.4 %, un percentil 99 del 11.2 % y un máximo del 19.4 %. Solo 5 de los 257 (1.9 %) superaron el 10 %. En los juegos reversibles, la mediana de activación recuperable fue del 46.7 %.

### 3.3 En una población heterogénea, la recuperación tras activación fuerte depende del cociente XIAP:caspasa-3

Con variabilidad lognormal (CV 0.25) y un pulso de 90 min, el 69.0 % de las células normales quedó comprometido, el 21.2 % se recuperó tras activar caspasa-3 y el 9.8 % no llegó a activarla (Fig. 5). Las células recuperadas tras activación alcanzaron un pico mediano del ~40 % de su caspasa-3. El destino quedó estratificado por el cociente de producción XIAP:caspasa-3 de cada célula (Tabla 2).

**Tabla 2.** Destino por quintil del cociente XIAP:caspasa-3 (células normales, pulso de 90 min; n = 120 por quintil).

| Quintil (mediana del cociente) | Comprometidas | Recuperadas tras activar caspasa-3 | Nunca activadas |
|---|---|---|---|
| Q1 (0.64) | 100 % | 0 % | 0 % |
| Q2 (0.83) | 94 % | 6 % | 0 % |
| Q3 (0.99) | 82 % | 17 % | 2 % |
| Q4 (1.22) | 60 % | 32 % | 8 % |
| Q5 (1.62) | 9 % | 52 % | 39 % |

### 3.4 Sobreexpresar XIAP genera sobre todo resistencia, no anastasis

En el escenario con producción de XIAP × 2 sobrevivió el 91.7–99.7 % de las células, según la duración del pulso. Sin embargo, la mayoría no llegó a activar caspasa-3: con el pulso de 90 min, el 82.5 % nunca la activó y solo el 9.2 % se recuperó tras activarla (Fig. 5).

### 3.5 Con el estado molecular completo, el destino es casi perfectamente predecible en simulación

Validación agrupada por duración de pulso (células normales, n = 4800):

| Predictores | ROC-AUC | PR-AUC | Brier |
|---|---|---|---|
| Solo caspasa-3 activa (regresión logística) | 0.921 | 0.902 | 0.109 |
| 13 especies (regresión logística) | 0.938 | 0.932 | 0.086 |
| 13 especies (bosque aleatorio) | 0.992 | 0.993 | 0.038 |

Las variables más importantes del bosque aleatorio fueron la caspasa-3 activa, la caspasa-9 escindida, la XIAP libre y el complejo apoptosoma-caspasa-9 escindida. Son medidas exactas de un modelo determinista: indican qué variables contienen la información, no qué rendimiento cabe esperar con datos reales.

### 3.6 Módulo mitocondrial: la MOMP completa no es el punto de no retorno

**Albeck: el modelo no tiene un estado de supervivencia.** En EARM, la activación de Bax por tBid es catalítica, el Bax activado no se inactiva, los poros mitocondriales no se cierran y no hay síntesis ni degradación de proteínas. Por construcción, para cualquier cantidad de tBid mayor que 0 todo el Bax acaba activándose, y la cantidad de Bax (100 000 moléculas) supera a la de Bcl-2 mitocondrial (20 000), por lo que acaban formándose poros. En las simulaciones, inhibir la caspasa-8 retrasó la muerte sin evitarla:

| Momento de la inhibición (ligando por defecto) | tBid en ese momento | Resultado |
|---|---|---|
| 1.0 h | 25.6 moléculas | muerte a las 22.4 h |
| 1.5 h | 79 moléculas | muerte a las 10.2 h |
| 0.5 h | 4.1 moléculas | 40 % de PARP escindida a las 96 h, en aumento |
| ≤ 0.25 h | < 1 molécula | 0.2 % de PARP escindida a las 96 h |

El último caso solo aparenta supervivencia: es un artefacto de tratar como continua una cantidad inferior a una molécula. Sin inhibidor, la muerte ocurrió a las 3.65 h. En este modelo, por tanto, el compromiso se produce antes de cualquier liberación medible de citocromo c, y la anastasis no puede representarse.

**Bagci: una MOMP parcial es compatible con la supervivencia.** Con el estímulo umbral (bolo de caspasa-8 de 5.28 × 10⁻⁵ µM):

- la célula que sobrevive liberó hasta el **14.5 %** de su citocromo c mitocondrial (pico a los ~8 min) y alcanzó como máximo un **0.10 %** de la caspasa-3 del estado apoptótico;
- la célula que muere terminó con el 83 % del citocromo c liberado;
- ambas trayectorias permanecieron juntas, cerca del umbral, unas 7 h antes de separarse (Fig. 6).

El tamaño de la MOMP sobrevivible dependió del equilibrio Bcl-2/Bax/IAP (Tabla 3).

**Tabla 3.** Escenarios de producción en el modelo de Bagci.

| Escenario | Bolo umbral de caspasa-8 (µM) | Citocromo c liberado máximo en superviviente | Caspasa-3 máxima en superviviente (% del estado apoptótico) |
|---|---|---|---|
| Referencia | 5.3 × 10⁻⁵ | 14.5 % | 0.10 % |
| Bcl-2 × 4 | 1.6 × 10⁻⁴ | 19.0 % | 0.30 % |
| Bcl-2 × 8 | 1.8 × 10⁻³ | 32.6 % | 2.60 % |
| IAP × 8 | 1.0 × 10⁻⁴ | 24.5 % | 0.10 % |
| Bax × 0.25 | 2.6 × 10⁻³ | 31.5 % | 5.79 % |
| Bax × 8 | 1.8 × 10⁻⁶ | 6.7 % | 0.005 % |

**Muestreo global (Bagci, 1000 juegos, Fig. 7).** De 1000 juegos, 546 tuvieron un umbral de estímulo, 420 no alcanzaron el estado apoptótico con ningún bolo ensayado, 32 fueron hipersensibles (morían con el bolo mínimo) y 2 superaron el presupuesto de cálculo (`integration_failed`; se informan y no se analizan). En los 546 juegos con umbral, la MOMP sobrevivible varió mucho: mediana 1.5 %, percentil 90 28.7 %, percentil 99 77.9 %, máximo 91.4 %. 140 juegos (25.6 %) superaron el 10 % y 23 (4.2 %) el 50 %. La caspasa-3 máxima sobrevivible fue mucho menor: mediana 0.0005 % del estado apoptótico, percentil 90 1.05 %. Solo 16 juegos (2.9 %) superaron el 10 % (máximo 72.6 %). Las células que mueren terminaron con una mediana del 90.9 % del citocromo c liberado.

### 3.7 Contraste con datos reales: no concluyente

De los 13 genes del contraste principal, Xiap, Casp3 y Casp9 no superaron el umbral de expresión pre-registrado (media log2 ≥ 7.0) en la plataforma. El índice se calculó, por tanto, con 3 frenos (Bcl2, Cflar, Bfar) y 7 impulsores. I(t) fue prácticamente nulo en todos los tiempos (R0 −0.036; R3 −0.034; R6 −0.001; R24 −0.102; R48 +0.004), con p de Holm = 1.0 en los cuatro tiempos de recuperación (Fig. 8). Según el criterio fijado de antemano, el resultado es **no concluyente**: los datos no muestran el desplazamiento transcripcional hacia los inhibidores, y la ausencia de tres genes clave limita la prueba.

A nivel descriptivo, en la recuperación temprana (R3–R6) aumentaron a la vez genes antiapoptóticos (Mcl1, +0.80 log2 en R3; Cflar, +0.55 en R6) y proapoptóticos BH3-only (Bbc3/PUMA, +1.64 en R3; Pmaip1/NOXA, +0.82 en R3), mientras Bcl2 disminuyó (−0.68 a −0.93 entre R0 y R6). Ninguno de estos genes formaba parte de la hipótesis principal salvo Bcl2 y Cflar, y no los interpretamos como prueba.

## 4. Discusión

**El punto de no retorno precede a la activación masiva de caspasas y a la MOMP completa.** En los dos modelos con estado de supervivencia (Legewie y Bagci), la separatriz se cruza cuando la caspasa-3 activa es una fracción mínima de su máximo (< 3 % en Legewie; ≈ 0.1 % del estado apoptótico en Bagci) y, en Bagci, cuando se ha liberado solo un 15 % del citocromo c. Esto concuerda con que MOMP y activación de caspasas sean *consecuencias* del compromiso más que su causa. También indica que la "MOMP completa" no es el umbral que separa vida y muerte en estos modelos: una MOMP parcial es sobrevivible, en línea con la *minority MOMP* descrita por Ichim et al. [7] y la liberación subletal de citocromo c de Kalkavan et al. [9]. La analogía es solo a nivel de la fracción celular liberada: en el modelo, las mitocondrias forman un único compartimento homogéneo, mientras que en la *minority MOMP* se permeabiliza por completo un subconjunto de mitocondrias.

**La anastasis tras activación sustancial no cabe en los modelos sin heterogeneidad.** Los experimentos de anastasis describen la recuperación de la gran mayoría de las células tras fragmentación mitocondrial, activación de caspasa-3 y daño en el ADN [1], y la supervivencia tras activación de las caspasas efectoras 3/7 [5]. En los dos modelos con estado de supervivencia, una célula individual con PNR solo se recupera tras activar una fracción sustancial (> 10 %) de su caspasa-3 en una minoría de juegos de parámetros: el 1.9 % en Legewie y el 2.9 % en Bagci. Hay tres explicaciones compatibles con nuestros resultados, que no se excluyen entre sí:

1. **Heterogeneidad.** Las células que hacen anastasis podrían estar en el régimen reversible por su equilibrio inhibidor:efector, como en la Tabla 2. En ese caso, la anastasis sería una propiedad de subpoblaciones predecible por su estado previo.
2. **Procesos de reversión ausentes en los modelos.** Por ejemplo, la eliminación de mitocondrias permeabilizadas, la degradación de tBid o la reparación del daño. EARM ilustra el caso extremo: sin ningún proceso de reversión, cualquier tBid compromete a la célula.
3. **Un PNR fisiológico aguas abajo.** El compromiso real podría situarse en la escisión de sustratos críticos o en la pérdida de integridad celular, y no en el interruptor de caspasas.

**Implicaciones para el cáncer.** Sobreexpresar XIAP o Bcl-2, o reducir Bax, desplaza el umbral y amplía la MOMP sobrevivible (hasta el 33 % con Bcl-2 × 8). La consecuencia principal es un aumento de células que nunca activan caspasa-3 (resistencia). La fracción que activa caspasa-3 y se recupera (anastasis) crece más despacio, con pulsos largos. Para estudiar la "supervivencia tras tratamiento" conviene, por tanto, separar ambos fenómenos, que tienen biología y riesgos diferentes. La supervivencia con caspasa subletal o MOMP parcial se ha asociado experimentalmente a daño genómico y persistencia [7, 9], y en nuestros supervivientes la exposición acumulada a caspasa-3 alcanzó 195–492 nM·min (Tabla 1).

**Predicciones contrastables.**
- **P1.** A igual estímulo, las células con un cociente XIAP:procaspasa-3 previo alto deberían recuperarse tras activar caspasa-3 con más frecuencia que las de cociente bajo. Se puede contrastar con biosensores de caspasa [3] e inmunofluorescencia cuantitativa en célula individual.
- **P2.** La liberación parcial de citocromo c (≲ 15–30 %, según Bcl-2/Bax) debería ser compatible con la supervivencia. Se puede contrastar con reporteros de citocromo c o de Smac por mitocondria.
- **P3.** En tumores con XIAP o Bcl-2 elevados, la mayoría de las supervivientes a un tratamiento transitorio no debería tener historia de caspasa activa.

**Limitaciones.**
- Ningún modelo incluye la ejecución de la muerte, la reparación ni la regulación transcripcional; "comprometida" significa permanecer en el estado apoptótico del modelo.
- Ningún modelo incluye la muerte independiente de caspasas que suele seguir a la MOMP [7, 8]. La supervivencia con MOMP parcial del modelo de Bagci se refiere solo a la vía caspásica y podría sobrestimar la supervivencia real.
- Ningún modelo representa mitocondrias individuales, así que no distinguen una MOMP parcial homogénea de una *minority MOMP*.
- Los parámetros proceden de compilaciones in vitro y no están ajustados a los tipos celulares de los experimentos de anastasis. El modelo de Bagci no está curado, aunque reproduce cuatro cifras de su artículo con una diferencia máxima del 1.4 %.
- El CV de la variabilidad celular es un supuesto.
- La predicción del destino usa medidas exactas de un modelo determinista.
- El contraste con datos reales se limita a un conjunto bulk de microarrays: tres genes clave no se detectaron y no podía contrastar P1. El segundo conjunto disponible (GSE86480) no se pudo usar por falta de correspondencia entre columnas y muestras.

## 5. Conclusiones

1. En los modelos mecanísticos publicados de la apoptosis, el punto de no retorno se cruza, en la gran mayoría de los parámetros explorados, con una fracción mínima de caspasa-3 activa y antes de la MOMP completa.
2. Su posición depende del equilibrio entre inhibidores (XIAP, Bcl-2) y efectores (caspasas, Bax). En una población heterogénea, ese equilibrio determina qué células pueden recuperarse tras activar caspasa-3.
3. La anastasis tras activación sustancial de caspasas, observada experimentalmente, solo aparece en una minoría (< 3 %) de los parámetros de estos modelos. Su frecuencia experimental sugiere heterogeneidad celular, mecanismos de reversión no modelados o un punto de no retorno situado aguas abajo.
4. Un contraste pre-registrado con datos transcriptómicos públicos no encontró el desplazamiento hacia los inhibidores que planteaba la hipótesis (no concluyente). La prueba decisiva requiere medidas en célula individual.

## Disponibilidad de datos y código

- Código, modelos SBML, resultados y figuras: `research/` del repositorio del proyecto.
- Experimentos de caspasas: `python -m simulation.run_cpnr_simulations`.
- Módulo mitocondrial: `python -m simulation.run_momp_simulations`.
- Contraste con datos reales: `python -m evaluation.gse90959_brake_driver`.
- Tests: `python -m pytest tests -q` (11 tests).
- Inventario, hashes y versiones de software: Material suplementario S1 (`Documentacion/simulacion_cpnr_resultados.md`, sección 7).
- Datos públicos: GEO GSE90959; BioModels BIOMD0000000102, BIOMD0000000103, BIOMD0000000220 y MODEL1006230056.

## Declaración sobre el uso de inteligencia artificial

La implementación del código, la ejecución de las simulaciones, la verificación bibliográfica y la redacción de este borrador se realizaron con asistencia de un modelo de lenguaje (Claude, Anthropic), bajo la dirección de los autores. Todas las cifras proceden de código ejecutable incluido en el repositorio. Las referencias se verificaron en Europe PMC, Crossref o el texto original. Los autores deben revisar y asumir la responsabilidad del contenido final.

## Figuras

- **Figura 1.** Histéresis de caspasa-3 frente a la entrada de apoptosoma en los modelos WT y NC de Legewie. `research/figures/E1_histeresis_WT_vs_NC.png`
- **Figura 2.** Izquierda: trayectorias justo por debajo y por encima de T\*. Derecha: frontera del PNR en función de la intensidad del estímulo. `research/figures/E2_punto_no_retorno_WT.png`
- **Figura 3.** Ventana de anastasis y T\* frente a la producción de XIAP y la degradación de caspasa-3 activa. `research/figures/E3_ventana_anastasis_XIAP_degradacion.png`
- **Figura 4.** Muestreo global del modelo de Legewie: regímenes y ventana de anastasis. `research/figures/E3b_robustez_global.png`
- **Figura 5.** Destino en poblaciones heterogéneas, normales y con XIAP × 2. `research/figures/E4_poblacion_supervivencia.png`
- **Figura 6.** Modelo de Bagci: liberación de citocromo c y caspasa-3 junto al umbral. `research/figures/M2_bagci_MOMP_parcial_umbral.png`
- **Figura 7.** Muestreo global del modelo de Bagci. `research/figures/M4_bagci_robustez_global.png`
- **Figura 8.** GSE90959: frenos e impulsores del interruptor e índice pre-registrado. `research/figures/D1_GSE90959_frenos_impulsores.png`

## Referencias

1. Tang HL, Tang HM, Mak KH, Hu S, Wang SS, Wong KM, et al. Cell survival, DNA damage, and oncogenic transformation after a transient and reversible apoptotic response. *Mol Biol Cell*. 2012;23:2240–2252. doi:10.1091/mbc.e11-11-0926. PMID 22535522.
2. Tang HM, Tang HL. Anastasis: recovery from the brink of cell death. *R Soc Open Sci*. 2018;5:180442. doi:10.1098/rsos.180442. PMID 30839720.
3. Tang HL, Tang HM, Fung MC, Hardwick JM. In vivo CaspaseTracker biosensor system for detecting anastasis and non-apoptotic caspase activity. *Sci Rep*. 2015;5:9015. doi:10.1038/srep09015. PMID 25757939.
4. Ding X, Sun G, Argaw YG, Wong JO, Easwaran S, Montell DJ. CasExpress reveals widespread and diverse patterns of cell survival of caspase-3 activation during development in vivo. *eLife*. 2016;5:e10936. doi:10.7554/eLife.10936. PMID 27058168.
5. Sun G, Guzman E, Balasanyan V, Conner CM, Wong K, Zhou HR, et al. A molecular signature for anastasis, recovery from the brink of apoptotic cell death. *J Cell Biol*. 2017;216:3355–3368. doi:10.1083/jcb.201706134. PMID 28768686.
6. Tang HM, Talbot CC, Fung MC, Tang HL. Transcriptomic study of anastasis for reversal of ethanol-induced apoptosis in mouse primary liver cells. *Sci Data*. 2022;9:418. doi:10.1038/s41597-022-01470-8. PMID 35851273.
7. Ichim G, Lopez J, Ahmed SU, Muthalagu N, Giampazolias E, Delgado ME, et al. Limited mitochondrial permeabilization causes DNA damage and genomic instability in the absence of cell death. *Mol Cell*. 2015;57:860–872. doi:10.1016/j.molcel.2015.01.018. PMID 25702873.
8. Tait SWG, Green DR. Mitochondria and cell death: outer membrane permeabilization and beyond. *Nat Rev Mol Cell Biol*. 2010;11:621–632. doi:10.1038/nrm2952. PMID 20683470.
9. Kalkavan H, Chen MJ, Crawford JC, Quarato G, Fitzgerald P, Tait SWG, et al. Sublethal cytochrome c release generates drug-tolerant persister cells. *Cell*. 2022;185:3356–3374.e22. doi:10.1016/j.cell.2022.07.025. PMID 36055199.
10. Wang R, Wang Y, Liu X, Liu M, Sun L, Pan X, et al. Anastasis enhances metastasis and chemoresistance of colorectal cancer cells through upregulating cIAP2/NFκB signaling. *Cell Death Dis*. 2023;14:388. doi:10.1038/s41419-023-05916-8. PMID 37391410.
11. Legewie S, Blüthgen N, Herzel H. Mathematical modeling identifies inhibitors of apoptosis as mediators of positive feedback and bistability. *PLoS Comput Biol*. 2006;2:e120. doi:10.1371/journal.pcbi.0020120. PMID 16978046.
12. Albeck JG, Burke JM, Aldridge BB, Zhang M, Lauffenburger DA, Sorger PK. Quantitative analysis of pathways controlling extrinsic apoptosis in single cells. *Mol Cell*. 2008;30:11–25. doi:10.1016/j.molcel.2008.02.012. PMID 18406323.
13. Albeck JG, Burke JM, Spencer SL, Lauffenburger DA, Sorger PK. Modeling a snap-action, variable-delay switch controlling extrinsic cell death. *PLoS Biol*. 2008;6:2831–2852. doi:10.1371/journal.pbio.0060299. PMID 19053173.
14. Bagci EZ, Vodovotz Y, Billiar TR, Ermentrout GB, Bahar I. Bistability in apoptosis: roles of bax, bcl-2, and mitochondrial permeability transition pores. *Biophys J*. 2006;90:1546–1559. doi:10.1529/biophysj.105.068122. PMID 16339882.
15. Hucka M, Finney A, Sauro HM, Bolouri H, Doyle JC, Kitano H, et al. The systems biology markup language (SBML): a medium for representation and exchange of biochemical network models. *Bioinformatics*. 2003;19:524–531. doi:10.1093/bioinformatics/btg015. PMID 12611808.
16. Malik-Sheriff RS, Glont M, Nguyen TVN, Tiwari K, Roberts MG, Xavier A, et al. BioModels—15 years of sharing computational models in life science. *Nucleic Acids Res*. 2020;48:D407–D415. doi:10.1093/nar/gkz1055. PMID 31701150.
17. Virtanen P, Gommers R, Oliphant TE, Haberland M, Reddy T, Cournapeau D, et al. SciPy 1.0: fundamental algorithms for scientific computing in Python. *Nat Methods*. 2020;17:261–272. doi:10.1038/s41592-019-0686-2. PMID 32015543.
18. Eissing T, Conzelmann H, Gilles ED, Allgöwer F, Bullinger E, Scheurich P. Bistability analyses of a caspase activation model for receptor-induced apoptosis. *J Biol Chem*. 2004;279:36892–36897. doi:10.1074/jbc.M404893200. PMID 15208304.
19. Waldherr S, Eissing T, Chaves M, Allgöwer F. Bistability preserving model reduction in apoptosis. arXiv:q-bio/0702011 (2007).
20. Sigal A, Milo R, Cohen A, Geva-Zatorsky N, Klein Y, Liron Y, et al. Variability and memory of protein levels in human cells. *Nature*. 2006;444:643–646. doi:10.1038/nature05316. PMID 17122776.
21. Spencer SL, Gaudet S, Albeck JG, Burke JM, Sorger PK. Non-genetic origins of cell-to-cell variability in TRAIL-induced apoptosis. *Nature*. 2009;459:428–432. doi:10.1038/nature08012. PMID 19363473.
22. Edgar R, Domrachev M, Lash AE. Gene Expression Omnibus: NCBI gene expression and hybridization array data repository. *Nucleic Acids Res*. 2002;30:207–210. doi:10.1093/nar/30.1.207. PMID 11752295.
23. Holm S. A simple sequentially rejective multiple test procedure. *Scand J Stat*. 1979;6(2):65–70.
24. Benjamini Y, Hochberg Y. Controlling the false discovery rate: a practical and powerful approach to multiple testing. *J R Stat Soc Series B Stat Methodol*. 1995;57:289–300. doi:10.1111/j.2517-6161.1995.tb02031.x.
