# Smart Money Flow Cloud: investigación y versión validada

Análisis del indicador "Smart Money Flow Cloud [BOSWaves]", con mejoras de señal medidas sobre 68 series reales (cripto, acciones, ETF y futuros; 1h, 4h y 1d), validación fuera de muestra y versión `strategy()`.

**Empieza por [`INFORME.md`](INFORME.md)**: conclusiones, tablas y respuestas a las 8 preguntas.

## Estructura

| Ruta | Contenido |
|---|---|
| `pine/00_original_smf_cloud.pine` | Indicador original (referencia, sin cambios). |
| `pine/01_smf_cloud_senales_validadas.pine` | **Indicador mejorado**: entradas con filtro de volatilidad, continuación, pullback, cambios tardíos, salidas, stop, panel y alertas. |
| `pine/02_smf_cloud_estrategia.pine` | **Versión `strategy()`**: largos y cortos, comisión, slippage, stop, salida configurable, tamaño (% del capital, riesgo % o cantidad fija) y rango de fechas. |
| `INFORME.md` | Informe completo. |
| `resultados/*.csv, *.md` | Todas las tablas generadas (IS = desarrollo, OOS = validación). |
| `resultados/figuras/` | Gráficos: original vs nuevo sobre datos reales, efecto de la volatilidad y Sharpe OOS. |
| `research/` | Código Python reproducible (ver abajo). |

## Uso en TradingView

1. Abre el Editor de Pine, pega el contenido de `pine/01_…` (indicador) o `pine/02_…` (estrategia) y pulsa *Añadir al gráfico*.
2. Crea las alertas con la opción **"Una vez por cierre de vela"**.
3. Ajustes recomendados según los resultados:
   - **Acciones/ETF:** desactiva los cortos.
   - **Cripto 4h/1d:** umbral de compresión 1,1–1,2 y tamaño por riesgo 1–2%.
   - **Cripto 1h o menos:** no recomendado con comisiones *taker*; la ventaja bruta ≈ los costes.

## Reproducir la investigación

```bash
pip install pandas numpy numba matplotlib requests yfinance tabulate
cd research
python data.py                  # descarga Binance (cripto) y Yahoo (acciones) a research/data/ (no versionado)
python tests/test_backtest.py   # semántica del backtester (ejecución, stops, gaps, parciales, costes)
python pine_mirror.py           # la transliteración del Pine produce las mismas operaciones que system.py
python study_basis_test.py is   # retroceso vs reversión en el test de la base
python study_entries.py is      # variantes de entrada (y 'oos')
python study_conditions.py is   # condicionantes (volatilidad, flujo, pendiente...)
python study_exits.py is        # salidas por separado (y 'oos')
python study_robustness.py is   # sensibilidad de parámetros (y 'oos')
python study_timing.py is       # retraso, % recorrido, falsas, cobertura (y 'oos')
python validate.py oos          # escalera original → final, cartera, por año (añade '2.0' para costes x2)
python study_significance.py    # t-stat con agregación mensual
python charts.py                # figuras
```

Módulos principales:

| Módulo | Qué hace |
|---|---|
| `smf.py` | Port fiel del indicador con semántica de Pine. |
| `labels.py`, `evaluate.py` | Verdad de campo: zigzag ATR, triple barrera y métricas de señal. |
| `signals.py` | Familias de señales candidatas. |
| `system.py` | **Sistema configurable** (fuente de verdad del Pine mejorado). |
| `backtest.py` | Motor que replica `strategy()`. |

Nota: los datos de Binance y Yahoo no son idénticos a los de TradingView, así que los números en TradingView serán parecidos pero no iguales.

## Licencia

El código Pine es una obra derivada del original de BOSWaves y se distribuye bajo la **Mozilla Public License 2.0**, como el original (ver la cabecera de cada archivo).
