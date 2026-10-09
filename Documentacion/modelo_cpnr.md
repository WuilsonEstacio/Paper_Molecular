# Modelo CPNR: Cellular Point of No Return

## Objetivo
Definir un marco conceptual y computacional para estimar la transición entre daño celular reversible, compromiso apoptótico y muerte irreversible, usando evidencia bibliográfica y datos experimentales/ómicos cuando estén disponibles.

## Hipótesis operativa
La frontera entre recuperación y muerte no depende de un biomarcador único, sino de una combinación temporal de:

- ATP
- ΔΨm
- ROS
- Ca²⁺
- MOMP
- cytochrome c
- caspasas
- daño de ADN
- integridad de membrana
- mitophagy
- proteostasis
- transcripción

## Estados propuestos

- S0 = Healthy
- S1 = Stress
- S2 = Reversible Injury
- S3 = Severe Reversible Injury
- S4 = Apoptotic Commitment
- S5 = Anastasis
- S6 = Irreversible Death
- S7 = Recovered but Genomically Damaged

### Estados tumorales

- C0 = Cancer Viable
- C1 = Cancer Under Stress
- C2 = Apoptosis Initiated
- C3 = Cancer Anastasis
- C4 = Cancer Irreversible Death
- C5 = Resistant Survivor

## Variables candidatas

| Variable | Rol esperado |
| --- | --- |
| ATP | bioenergética y viabilidad |
| ΔΨm | función mitocondrial |
| ROS | estrés oxidativo |
| Ca²⁺ | homeostasis y señalización de muerte |
| MOMP | compromiso mitocondrial |
| cytochrome c | activación apoptótica |
| caspase-3/7/8/9 | ejecución apoptótica |
| DNA damage | daño genómico acumulado |
| membrane integrity | integridad celular |
| mitophagy | capacidad de reparación mitocondrial |
| proteostasis | resiliencia celular |
| transcription | recuperación de programas de supervivencia |

## Función objetivo

P(Recovery | CellularState)

P(IrreversibleDeath | CellularState)

P(UnsafeRecovery | CellularState)

Para cáncer:

P(CancerAnastasis)

P(ResistanceAfterRecovery)

## Arquitectura de modelado propuesta

1. Capa mecanística: ecuaciones / redes de señalización.
2. Capa de estado: transición entre S0–S7 o C0–C5.
3. Capa predictiva: modelos interpretables (logistic regression, random forest, XGBoost, LightGBM).
4. Capa explicable: SHAP, feature importance, partial dependence.

## Reglas metodológicas

- No usar datos del mismo experimento en train y test sin agrupación.
- Preferir GroupKFold / leave-one-study-out.
- No mezclar datos simulados con datos reales sin etiquetado explícito.
- Marcar parámetros no identificados como UNIDENTIFIED_PARAMETER.
- Toda conclusión debe distinguir: experimental, computacional, inferencia, hipótesis.

## Interpretación biológica

El CPNR no se define como un único punto universal, sino como un conjunto de umbrales dependientes del tipo celular, el estímulo y el contexto biológico.
