# Como contribuir

Gracias por su interes. Este es un proyecto de investigacion doctoral en curso; las contribuciones
son bienvenidas a traves de *issues* y *pull requests*.

## Reglas cientificas del proyecto

Toda contribucion debe respetar las reglas que rigen el proyecto:

1. **No inventar constantes.** Los modelos usan parametros publicados y verificables. Un parametro sin
   fuente se marca como `UNIDENTIFIED_PARAMETER` y no se presenta como dato.
2. **Etiquetar la procedencia.** Todo dato o resultado lleva `data_provenance`: `REAL`, `SIMULATED` o `DERIVED`.
   Los datos simulados no se usan nunca como evidencia experimental.
3. **Pre-registrar los contrastes con datos reales.** Hipotesis, conjuntos y prueba se fijan antes de
   calcular resultados (ver `Documentacion/preregistro_GSE90959.md`).
4. **Informar los resultados negativos y no concluyentes** igual que los positivos.
5. **Trazabilidad.** Cada cifra de un documento debe poder rastrearse a un archivo y una columna.
   Si cambia el codigo, actualice los hashes de `Documentacion/simulacion_cpnr_resultados.md` (seccion 7).

## Flujo de trabajo

1. Abra un *issue* describiendo el cambio o el problema.
2. Cree una rama, haga el cambio y ejecute los tests:
   ```bash
   cd research
   python -m pytest tests -q
   ```
3. Si el cambio afecta a resultados, vuelva a ejecutar el script correspondiente e incluya las tablas y
   figuras regeneradas en el *pull request*.
4. No suba PDF de articulos con derechos de autor, datos privados, credenciales ni rutas locales.

## Reportar errores cientificos

Si encuentra una cifra, cita o afirmacion que no se sostiene con los archivos del repositorio, abra un
*issue* indicando el documento, la seccion y el archivo de resultados que la contradice.
