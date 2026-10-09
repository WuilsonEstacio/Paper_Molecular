# Simplified Cellular Injury Digital Twin

## Propósito
Representar de forma simplificada la evolución temporal de una célula sometida a estrés o daño, integrando evidencia biomédica real, modelos mecanísticos y machine learning.

## Qué representa

- transiciones de estado celular
- variables moleculares y morfológicas observables
- trayectorias de recuperación, anastasis o muerte irreversible
- riesgo diferencial en contexto tumoral

## Qué no representa

- una célula humana completa
- una simulación exhaustiva de toda la bioquímica celular
- validación clínica
- una prueba de que células muertas irreversiblemente puedan revivir

## Estados conceptuales

HEALTHY -> STRESS -> REVERSIBLE_INJURY -> SEVERE_REVERSIBLE_INJURY -> APOPTOTIC_COMMITMENT -> {ANASTASIS, RECOVERY, IRREVERSIBLE_DEATH}

Para cáncer:

CANCER_VIABLE -> TREATMENT_STRESS -> APOPTOSIS_INITIATED -> {ANASTASIS, RESISTANT_SURVIVOR, CELL_DEATH}

## Capas del gemelo

1. Datos biomédicos reales
2. Extracción de características
3. Vector de estado celular
4. Modelos mecanísticos (PySB/BioNetGen)
5. Simulación multicelular (PhysiCell)
6. ML predictivo
7. Validación externa

## Estado actual

- Biblioteca científica core depurada: sí
- Catálogo de datasets reales: inicial, priorizado y en expansión
- Modelos mecanísticos: núcleo caspasa-9/caspasa-3/XIAP de Legewie et al. 2006 (SBML curado, BIOMD0000000102/103) operativo, con experimentos de punto de no retorno E1–E5 (ver `simulacion_cpnr_resultados.md`); scaffolds BioNetGen/PySB siguen vacíos
- Simulación multicelular: scaffold PhysiCell preparado
- ML baseline: pipeline técnico validado, pendiente de datos reales

## Estado de BioNeMo

- BIONEMO_STATUS: NOT_REQUIRED por ahora
- se reevaluará si aparecen tareas claras de protein embeddings o drug-target prediction

## Variables candidatas

- ATP
- ROS
- Ca2+
- DeltaPsiM
- MOMP
- CytochromeC
- Caspase3
- Caspase8
- Caspase9
- DNA_damage
- MembraneIntegrity
- Mitophagy
- Autophagy
- Proteostasis
- transcription_state
- morphology

## Principio metodológico

Los datos sintéticos solo se usan para pruebas técnicas, sensibilidad, Monte Carlo o exploración mecanística. La evidencia principal debe provenir de datos biomédicos reales.
