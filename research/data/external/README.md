# Datos externos

## SYNTHETIC_EXAMPLE_cpnr_dataset.csv

Este archivo contiene 6 filas escritas a mano únicamente para validar el esquema de columnas
del pipeline (`ATP`, `DeltaPsiM`, `ROS`, ... `label`, `study_id`). No proviene de ningún
experimento, dataset público ni artículo. Todas las filas están marcadas `data_provenance=SIMULATED`.

**No debe usarse para entrenar ni reportar métricas reales.** `research/src/evaluation/run_validation.py`
rechaza cualquier archivo que no tenga la columna `data_provenance` con valores `REAL` o `SIMULATED`
declarados explícitamente, y además exige un mínimo de filas y grupos (`study_id`) antes de calcular
cualquier métrica, precisamente para evitar que este archivo de ejemplo se use como si fuera evidencia.

Cuando la Fase 7 del plan (`Documentacion/` — búsqueda de datasets públicos) identifique datos reales
utilizables, deben ir en `research/data/raw/` (crudos) y `research/data/processed/` (procesados), nunca
mezclados con este archivo de ejemplo.
