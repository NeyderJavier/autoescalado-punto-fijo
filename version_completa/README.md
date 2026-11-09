# Versión completa: autoescalado con 5 métodos numéricos

Proyecto de Análisis Numérico. Un panel tipo DevOps calcula, minuto a minuto, cuántas réplicas (CPU y RAM) asignar a un servicio en la nube. El tráfico crece de forma exponencial o logarítmica, y el objetivo es que el clúster trabaje al **80 %** de su capacidad computacional y térmica.

## Instalación y ejecución

```bash
python -m venv venv
venv\Scripts\activate            # Windows   (Linux/Mac: source venv/bin/activate)
pip install -r requirements.txt

streamlit run app.py             # panel interactivo en el navegador
python demo_consola.py           # análisis completo en consola + figuras en resultados/
python -m pytest -v              # 49 pruebas automáticas
```

## El problema matemático

La capacidad real de N réplicas sigue la **Ley de Escalabilidad Universal**, con una penalización térmica η(N):

    X_eff(N) = X₁·N·η(N) / (1 + σ(N−1) + κN(N−1))

Ecuación de balance:  **ρ·X_eff(N) = λ(t)**. En forma de punto fijo:

    N = g(N) = λ·(1 + σ(N−1) + κN(N−1)) / (ρ·X₁·η(N))

**Resultado clave:** |g′(N*)| < 1 se cumple exactamente cuando añadir réplicas todavía aumenta la capacidad. Si el tráfico supera λ_máx, el método diverge, y esa divergencia corresponde físicamente a la saturación del clúster.

## Métodos numéricos usados (todos implementados desde cero)

| Para qué | Método |
|---|---|
| Resolver la ecuación de balance | Punto fijo, Steffensen (Aitken Δ²), Newton-Raphson, Secante, Bisección |
| Encontrar el pico de capacidad (λ_máx) | Sección dorada |
| Pronosticar el tráfico (escalado predictivo) | Mínimos cuadrados + eliminación de Gauss |
| Estimar el orden de convergencia | p ≈ ln(eₖ₊₁/eₖ) / ln(eₖ/eₖ₋₁) |

## Estructura

```
app.py                  Interfaz Streamlit (5 pestañas)
demo_consola.py         Ejecución sin interfaz, exporta tablas y figuras
nucleo/
  modelo.py             Tráfico, USL, modelo térmico, derivadas analíticas, recursos
  metodos.py            Métodos numéricos genéricos
  balance.py            Une el modelo con los métodos
  prediccion.py         Mínimos cuadrados + Gauss
  simulador.py          Simulación: arranque en frío, cooldown, reactivo/predictivo, costos
  graficas.py           Figuras matplotlib
datos/trafico_ejemplo.csv   Tráfico SINTÉTICO de ejemplo (formato: minuto, req_s)
tests/test_metodos.py   Validación contra scipy.optimize.brentq
resultados/             Figuras y CSV generados por demo_consola.py
```

## Pestañas del panel

1. **Panel en vivo:** KPIs (réplicas, vCPU, RAM, utilización, temperatura, iteraciones), gráficas, registro de eventos y botón para reproducir la simulación.
2. **Métodos numéricos:** comparación de los 5 métodos (iteraciones, evaluaciones, orden), diagrama de telaraña y tabla de iteraciones.
3. **Reactivo vs predictivo:** peticiones perdidas frente a costo cuando los contenedores tardan en arrancar.
4. **Análisis de convergencia:** curva de capacidad, g′(N*) frente a λ y mapa de la región de convergencia.
5. **Fundamento teórico:** todas las ecuaciones.

Los valores de σ, κ, X₁ y el modelo térmico son supuestos razonables para la simulación, no mediciones de un servidor real. Si consigues datos reales de tráfico (por ejemplo, logs públicos de servidores web), cárgalos como CSV en la barra lateral.
