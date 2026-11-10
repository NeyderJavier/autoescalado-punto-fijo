"""Dibujos de cada método: la curva real y las figuras con que se aproxima el área."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

COLOR = {"Trapecio": "#2563eb", "Simpson 1/3": "#16a34a", "Simpson 3/8": "#9333ea"}
CURVA = "#111827"

plt.rcParams.update({"axes.spines.top": False, "axes.spines.right": False, "axes.grid": True,
                     "grid.alpha": .3, "font.size": 11, "legend.frameon": False})


def _segmentos(metodo, n):
    """Cuántos puntos usa cada figura: 2 (recta), 3 (parábola) o 4 (cúbica)."""
    return {"Trapecio": 1, "Simpson 1/3": 2, "Simpson 3/8": 3}[metodo]


def dibujar(p, metodo, n, alto=4.3, hasta=None):
    """Curva real (negra) + figuras del método (coloreadas).
    hasta: si se indica, solo se dibujan las primeras `hasta` figuras (para la animación)."""
    fig, ax = plt.subplots(figsize=(8, alto), dpi=110)
    x = np.linspace(p.a, p.b, 500)
    h = (p.b - p.a) / n
    xs = p.a + h * np.arange(n + 1)
    ys = p.f(xs)
    color = COLOR[metodo]
    paso = _segmentos(metodo, n)

    total = n // paso
    for j, k in enumerate(range(0, n, paso)):
        if hasta is not None and j >= hasta:
            break
        actual = hasta is not None and j == hasta - 1
        xi = xs[k:k + paso + 1]
        yi = ys[k:k + paso + 1]
        coef = np.polyfit(xi, yi, len(xi) - 1)     # recta, parábola o cúbica por esos puntos
        xx = np.linspace(xi[0], xi[-1], 80)
        yy = np.polyval(coef, xx)
        alfa = .55 if actual else (.28 if j % 2 == 0 else .16)
        ax.fill_between(xx, yy, alpha=alfa, color=color, lw=0)
        ax.plot(xx, yy, color=color, lw=2.6 if actual else 1.8)
        if hasta is not None:
            ax.text((xi[0] + xi[-1]) / 2, float(np.max(yy)) * 0.45, str(j + 1), ha="center",
                    va="center", fontsize=12, fontweight="bold", color="white" if actual else color)
        ax.plot([xi[-1], xi[-1]], [0, yi[-1]], color=color, lw=.8, alpha=.6)
    ax.plot([xs[0], xs[0]], [0, ys[0]], color=color, lw=.8, alpha=.6)

    ax.plot(x, p.f(x), color=CURVA, lw=2, label="curva real")
    visibles = n + 1 if hasta is None else min(n + 1, hasta * paso + 1)
    ax.plot(xs[:visibles], ys[:visibles], "o", color=color, ms=6, zorder=5, label=f"{n + 1} puntos medidos")
    figura = {"Trapecio": "trapecios (rectas)", "Simpson 1/3": "parábolas", "Simpson 3/8": "cúbicas"}[metodo]
    ax.fill_between([], [], color=color, alpha=.3, label=f"área con {figura}")
    ax.set_xlabel(p.eje_x); ax.set_ylabel(p.eje_y)
    ax.set_ylim(bottom=min(0, float(np.min(p.f(x))) * 1.1))
    if p.invertir_y:
        ax.invert_yaxis()
    ax.legend(loc="best", fontsize=9)
    fig.tight_layout()
    return fig


def errores_vs_n(p, metodos, ns):
    """Error de cada método al aumentar n (escala logarítmica)."""
    fig, ax = plt.subplots(figsize=(8, 4.2), dpi=110)
    for m in metodos:
        errs = [abs(m.integrar(p.f, p.a, p.b, n) - p.exacta) for n in ns]
        errs = [max(e, 1e-16) for e in errs]
        ax.loglog(ns, errs, "o-", color=COLOR[m.NOMBRE], lw=2, label=m.NOMBRE)
    ax.set_xlabel("n (número de subintervalos)")
    ax.set_ylabel("error absoluto")
    ax.set_xticks(ns); ax.set_xticklabels([str(n) for n in ns])
    ax.legend()
    fig.tight_layout()
    return fig
