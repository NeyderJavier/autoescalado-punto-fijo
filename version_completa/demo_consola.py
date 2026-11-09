"""
Ejecuta todo el análisis sin interfaz gráfica y guarda figuras y tablas.
Útil para el informe escrito.

    python demo_consola.py
"""
from pathlib import Path

import pandas as pd

from nucleo import balance as bl
from nucleo import graficas as gr
from nucleo import modelo as md
from nucleo import simulador as sm

SALIDA = Path("resultados")
SALIDA.mkdir(exist_ok=True)


def guardar(fig, nombre):
    fig.savefig(SALIDA / nombre, dpi=150)
    gr.plt.close(fig)
    print(f"  · {SALIDA / nombre}")


def main():
    s = md.ParametrosServidor()
    lim = bl.limites(s)
    print("=" * 72)
    print("AUTOESCALADO DE CONTENEDORES POR MÉTODOS NUMÉRICOS")
    print("=" * 72)
    print(f"Pico de capacidad (sección dorada, {lim.iter_dorada} iter.): N = {lim.n_pico:.4f}")
    print(f"Tráfico máximo sostenible al {s.rho:.0%}: λ_máx = {lim.lambda_max:,.2f} req/s\n")

    # 1. Comparación de métodos en tres niveles de carga
    filas = []
    for lam in (300, 900, 0.95 * lim.lambda_max):
        for r, p in bl.comparar(lam, s, tol=1e-8):
            filas.append({"λ (req/s)": round(lam, 1), "Método": r.metodo, "N*": r.raiz,
                          "Iteraciones": r.n_iter, "Evaluaciones": r.evaluaciones,
                          "Orden estimado": p, "Tiempo (ms)": r.tiempo_ms,
                          "Convergió": r.convergio})
    tabla = pd.DataFrame(filas)
    print(tabla.to_string(index=False, float_format=lambda v: f"{v:.6g}"))
    tabla.to_csv(SALIDA / "comparacion_metodos.csv", index=False)

    # 2. Simulación reactiva vs predictiva
    trafico = md.serie_trafico(md.ParametrosTrafico(picos=[(90, 8, 1.6)]), 180)
    df_r = sm.simular(trafico, s, sm.ConfigSimulacion(estrategia="reactiva"))
    df_p = sm.simular(trafico, s, sm.ConfigSimulacion(estrategia="predictiva"))
    df_r.to_csv(SALIDA / "simulacion_reactiva.csv", index=False)
    df_p.to_csv(SALIDA / "simulacion_predictiva.csv", index=False)
    res = pd.DataFrame({"Reactiva": sm.resumen(df_r), "Predictiva": sm.resumen(df_p)})
    print("\nREACTIVA vs PREDICTIVA (180 min, pico ×1.6 en t=90)")
    print(res.to_string(float_format=lambda v: f"{v:,.2f}"))

    # 3. Figuras
    print("\nFiguras:")
    lam = 900
    rpf = bl.resolver(lam, s, "Punto fijo")
    guardar(gr.curva_capacidad(s, lam), "01_curva_capacidad.png")
    guardar(gr.telarana(lam, s, rpf), "02_telarana_punto_fijo.png")
    guardar(gr.errores([r for r, _ in bl.comparar(lam, s)], tol=1e-8), "03_errores_metodos.png")
    guardar(gr.convergencia_vs_lambda(s), "04_convergencia_vs_lambda.png")
    guardar(gr.mapa_sensibilidad(s), "05_mapa_sensibilidad.png")
    guardar(gr.trafico(df_p), "06_trafico_simulacion.png")
    guardar(gr.replicas(df_p), "07_replicas_simulacion.png")
    guardar(gr.utilizacion_temperatura(df_p, s), "08_utilizacion_temperatura.png")
    guardar(gr.comparar_estrategias(df_r, df_p), "09_reactiva_vs_predictiva.png")
    guardar(gr.iteraciones_tiempo(df_p), "10_warm_start.png")


if __name__ == "__main__":
    main()
