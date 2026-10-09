# Pre-registro del contraste con datos reales: GSE90959

Escrito el 2026-10-08, **antes** de calcular ningun resultado de expresion sobre estos datos.
Solo se habian inspeccionado el diseno (metadatos GEO) y el formato de los valores.
El hash SHA-256 de este archivo se registra en `simulacion_cpnr_resultados.md` para fijar su contenido.

## Datos

GSE90959 (Tang HM, Talbot CC, Fung MC, Tang HL. *Sci Data* 2022, PMID 35851273).
Hepatocitos primarios de raton. Tratamiento: etanol 4.5 % durante 5 h, lavado y recuperacion.
Grupos (n = 3 cada uno): Ctrl, R0 (fin del etanol), R3, R6, R24, R48 (horas de recuperacion).
Plataforma Illumina MouseWG-6 v2.0 (GPL6887). Valores del autor: BeadStudio, normalizacion por promedio, log2.

**Excluido: GSE86480** (Sun et al. 2017, HeLa, RNA-seq). Las columnas de su tabla de expresion
(`001-102`, `002-96`...) no tienen correspondencia publicada con las muestras GSM ni con las condiciones
(revisados los metadatos de GEO y de SRA/ENA). Asignarlas por agrupamiento seria inventar el diseno.

## Hipotesis derivada de las simulaciones

En las simulaciones (Legewie 2006, Bagci 2006), lo que controla la posicion del punto de no retorno
es el equilibrio entre los frenos del interruptor apoptotico (XIAP, BCL-2) y sus impulsores (caspasas,
Apaf-1, Bax, Bid, citocromo c). Subir la produccion de los frenos desplaza o elimina el punto de no
retorno. **Pregunta:** durante la recuperacion tras retirar el estimulo, ¿las celulas desplazan
transcripcionalmente ese equilibrio hacia los frenos?

**Prediccion direccional:** indice frenos-impulsores I(t) > 0 en la recuperacion (R3, R6, R24, R48) frente a Ctrl.

Esto pone a prueba una *hipotesis inspirada* por las simulaciones, no una salida directa de ellas:
los modelos no incluyen transcripcion regulada.

## Conjuntos de genes (fijados ahora; solo especies presentes en los tres modelos)

- **Frenos:** Xiap, Bcl2, Cflar (FLIP, Albeck), Bfar (BAR, Albeck).
- **Impulsores:** Casp3, Casp9, Apaf1, Casp8, Bid, Bax, Cycs, Diablo (Smac), Casp6.
- **Exploratorio, fuera del contraste principal** (misma clase funcional, no estan en los modelos):
  Birc2, Birc3, Bcl2l1, Mcl1, Bak1, Bbc3, Pmaip1.

## Metodo

1. Sonda → gen con la anotacion GPL6887. Si un gen tiene varias sondas, se usa la de mayor expresion media.
2. Genes expresados: media log2 >= 7.0 en el conjunto de las 18 muestras. Los genes de los conjuntos por
   debajo de ese umbral se informan, pero no entran en el indice.
3. log2FC(t) = media del grupo t − media de Ctrl.
4. I(t) = media(log2FC de los frenos) − media(log2FC de los impulsores).
5. Significacion: nulo empirico con 10 000 pares de conjuntos aleatorios del mismo tamano, tomados de los
   genes expresados (semilla 2026). p empirico bilateral. Correccion de Holm sobre los 4 tiempos de recuperacion.
6. Por gen: t de Welch frente a Ctrl en todos los genes expresados, FDR de Benjamini-Hochberg por tiempo.

## Que contara como resultado

- Apoyo: I(t) > 0 con p de Holm < 0.05 en al menos un tiempo de recuperacion y ningun tiempo con I(t) < 0 significativo.
- Contradiccion: I(t) < 0 significativo en la recuperacion.
- Cualquier otro caso: no concluyente. Se informara igual.

## Limitaciones conocidas de antemano

ARNm no es proteina. Las medidas son de poblacion (bulk), y los lavados pueden retirar celulas muertas, lo
que sesga hacia las supervivientes. El etanol no es un pulso de apoptosoma. n = 3 por grupo.
Esta prueba no puede contrastar la prediccion de celula individual (H1, cociente XIAP:caspasa-3 previo).
