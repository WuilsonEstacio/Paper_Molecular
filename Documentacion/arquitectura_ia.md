# Arquitectura de IA para Paper 1 y Paper 2

## Objetivo general
Construir un predictor de destino celular y riesgo de anastasis tumoral integrando evidencia mecanística, datos ómicos y, cuando sea posible, series temporales.

## Entrada esperada

- biomarcadores cuantitativos
- firmas transcriptómicas
- características morfológicas
- metadata del experimento
- contexto biológico (normal vs cáncer)

## Modelos prioritarios

1. Logistic Regression
2. Random Forest
3. XGBoost
4. LightGBM

## Modelos secundarios

- MLP
- redes temporales
- survival models

## Métricas

- ROC-AUC
- PR-AUC
- F1
- sensibilidad
- especificidad
- calibración
- Brier score

## Explicabilidad

- SHAP
- feature importance
- partial dependence

## Prevención de fuga de información

- GroupKFold
- StratifiedGroupKFold
- leave-one-study-out validation

## Salidas del sistema

- P(Recovery)
- P(IrreversibleDeath)
- P(UnsafeRecovery)
- P(CancerAnastasis)
- P(ResistanceAfterRecovery)

## Restricciones científicas

- No asumir que deep learning es superior.
- No usar datos sintéticos para validar el mismo generador.
- No extrapolar a clínica sin validación externa.
