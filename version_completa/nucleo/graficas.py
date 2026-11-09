"""Gráficas en matplotlib (estilo panel oscuro)."""
from __future__ import annotations

import math
from dataclasses import replace

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from . import balance as bl
from . import metodos as m
from . import modelo as md

FONDO, PANEL, LINEA, TXT, MUT = "#0b0f14", "#121820", "#243040", "#dbe4ee", "#8193a8"
VERDE, AZUL, AMBAR, ROJO, VIOLETA = "#3ddc97", "#4ea8ff", "#ffb547", "#ff5d6c", "#b18cff"
COLORES_METODO = {"Punto fijo": AMBAR, "Steffensen": VERDE, "Newton-Raphson": AZUL,
                  "Secante": VIOLETA, "Bisección": ROJO}

plt.rcParams.update({
    "figure.facecolor": PANEL, "axes.facecolor": PANEL, "savefig.facecolor": PANEL,
    "axes.edgecolor": LINEA, "axes.labelcolor": MUT, "text.color": TXT,
    "xtick.color": MUT, "ytick.color": MUT, "grid.color": LINEA, "grid.alpha": .7,
    "axes.grid": True, "legend.frameon": False, "font.size": 10,
    "axes.spines.top": False, "axes.spines.right": False,
})


def _fig(w=8, h=3.6):
    fig, ax = plt.subplots(figsize=(w, h), dpi=110)
    return fig, ax


def _sombrear_saturacion(ax, df):
    sat = df["saturado"].to_numpy()
    t = df["minuto"].to_numpy()
    i = 0
    while i < len(sat):
        if sat[i]:
            j = i
            while j + 1 < len(sat) and sat[j + 1]:
                j += 1
            ax.axvspan(t[i] - .5, t[j] + .5, color=ROJO, alpha=.12, lw=0)
            i = j + 1
        else:
            i += 1


# ---------------------------------------------------------------- simulación
def trafico(df, hasta=None):
    d = df if hasta is None else df[df["minuto"] <= hasta]
    fig, ax = _fig()
    _sombrear_saturacion(ax, d)
    ax.fill_between(d["minuto"], d["lambda"], color=AZUL, alpha=.12)
    ax.plot(d["minuto"], d["lambda"], color=AZUL, lw=1.8, label="Tráfico real λ(t)")
    if (d["lambda_plan"] != d["lambda"]).any():
        ax.plot(d["minuto"], d["lambda_plan"], color=VIOLETA, lw=1.2, ls=":", label="λ pronosticado (+margen)")
    ax.step(d["minuto"], d["capacidad_obj"], where="mid", color=VERDE, lw=1.6, ls="--", label="ρ·X(N) capacidad objetivo")
    ax.step(d["minuto"], d["capacidad"], where="mid", color=VERDE, lw=.8, alpha=.5, label="X(N) capacidad máxima")
    ax.set_xlabel("t (min)"); ax.set_ylabel("req/s"); ax.set_ylim(bottom=0)
    ax.legend(loc="upper left", fontsize=8)
    fig.tight_layout(); return fig


def replicas(df, hasta=None):
    d = df if hasta is None else df[df["minuto"] <= hasta]
    fig, ax = _fig()
    _sombrear_saturacion(ax, d)
    ax.fill_between(d["minuto"], d["activas"], step="mid", color=VERDE, alpha=.15)
    ax.step(d["minuto"], d["activas"], where="mid", color=VERDE, lw=1.8, label="Réplicas activas")
    ax.step(d["minuto"], d["activas"] + d["en_arranque"], where="mid", color=AMBAR, lw=1, ls="--",
            label="Activas + en arranque")
    ax.plot(d["minuto"], d["n_star"], color=TXT, lw=1, alpha=.8, label="N* (solución continua)")
    ax.set_xlabel("t (min)"); ax.set_ylabel("réplicas"); ax.set_ylim(bottom=0)
    ax.legend(loc="upper left", fontsize=8)
    fig.tight_layout(); return fig


def utilizacion_temperatura(df, s: md.ParametrosServidor, hasta=None):
    d = df if hasta is None else df[df["minuto"] <= hasta]
    fig, ax = _fig()
    ax.plot(d["minuto"], 100 * d["utilizacion"].clip(upper=1.5), color=AZUL, lw=1.5, label="Utilización real (%)")
    ax.axhline(100 * s.rho, color=VERDE, ls="--", lw=1, label=f"Objetivo {s.rho:.0%}")
    ax.axhline(100, color=ROJO, ls=":", lw=1, label="100 %")
    ax.set_ylabel("utilización (%)"); ax.set_xlabel("t (min)")
    ax2 = ax.twinx()
    ax2.plot(d["minuto"], d["temperatura"], color=AMBAR, lw=1.2, label="Temperatura (°C)")
    ax2.axhline(s.T_limite, color=AMBAR, ls=":", lw=.8)
    ax2.set_ylabel("°C", color=AMBAR); ax2.tick_params(colors=AMBAR); ax2.grid(False)
    ax2.spines["right"].set_visible(True)
    h1, l1 = ax.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, loc="upper left", fontsize=8, ncol=2)
    fig.tight_layout(); return fig


def iteraciones_tiempo(df):
    fig, ax = _fig()
    ax.plot(df["minuto"], df["iter_sin_warm"], color=MUT, lw=1, label="Semilla N₀ = λ/(ρX₁)")
    ax.plot(df["minuto"], df["iteraciones"], color=AMBAR, lw=1.5, label="Warm start (N* anterior)")
    ax.set_xlabel("t (min)"); ax.set_ylabel("iteraciones")
    ax.legend(fontsize=8); fig.tight_layout(); return fig


def comparar_estrategias(df_r, df_p):
    fig, axs = plt.subplots(1, 2, figsize=(10, 3.6), dpi=110)
    ax = axs[0]
    ax.plot(df_r["minuto"], df_r["lambda"], color=MUT, lw=1, label="Tráfico λ")
    ax.step(df_r["minuto"], df_r["capacidad"], where="mid", color=AMBAR, lw=1.4, label="Capacidad reactiva")
    ax.step(df_p["minuto"], df_p["capacidad"], where="mid", color=VERDE, lw=1.4, label="Capacidad predictiva")
    ax.set_xlabel("t (min)"); ax.set_ylabel("req/s"); ax.legend(fontsize=8); ax.set_title("Capacidad vs tráfico", fontsize=10)
    ax = axs[1]
    ax.plot(df_r["minuto"], df_r["perdidas"].cumsum(), color=AMBAR, lw=1.6, label="Reactiva")
    ax.plot(df_p["minuto"], df_p["perdidas"].cumsum(), color=VERDE, lw=1.6, label="Predictiva")
    ax.set_xlabel("t (min)"); ax.set_ylabel("peticiones"); ax.legend(fontsize=8)
    ax.set_title("Peticiones perdidas acumuladas", fontsize=10)
    fig.tight_layout(); return fig


# ---------------------------------------------------------------- métodos
def telarana(lam, s: md.ParametrosServidor, res: m.Resultado, x0=None, max_pasos=25):
    fig, ax = _fig(6.5, 5)
    x0 = md.n_inicial(lam, s) if x0 is None else x0
    xs = [x0] + [it.x for it in res.iteraciones[:max_pasos]]
    finitos = [v for v in xs if math.isfinite(v)]
    xmax = max(finitos) * 1.2 if res.convergio else min(max(finitos) * 1.2, bl.limites(s).n_pico * 2.5)
    xmax = max(xmax, 2)
    N = np.linspace(0, xmax, 400)
    ax.plot(N, md.g(N, lam, s), color=AZUL, lw=2, label="y = g(N)")
    ax.plot([0, xmax], [0, xmax], color=MUT, ls="--", lw=1, label="y = N")
    wx, wy = [xs[0]], [0]
    for a, b in zip(xs[:-1], xs[1:]):
        if not (math.isfinite(b) and b < xmax * 3):
            break
        wx += [a, b]; wy += [b, b]
    ax.plot(wx, wy, color=AMBAR, lw=1.1, marker="o", ms=2.5, label="Iteraciones")
    if res.convergio:
        ax.plot(res.raiz, res.raiz, "o", color=VERDE, ms=9, label=f"N* = {res.raiz:.4f}")
    ax.set_xlim(0, xmax); ax.set_ylim(0, xmax)
    ax.set_xlabel("N"); ax.set_ylabel("g(N)")
    ax.legend(fontsize=8, loc="upper left"); fig.tight_layout(); return fig


def errores(resultados: list[m.Resultado], tol=None):
    fig, ax = _fig(7, 4)
    for r in resultados:
        if not r.iteraciones:
            continue
        k = [it.k for it in r.iteraciones]
        e = [max(it.error_rel, 1e-17) for it in r.iteraciones]
        ax.semilogy(k, e, marker="o", ms=3, lw=1.5, color=COLORES_METODO.get(r.metodo, TXT),
                    label=f"{r.metodo} ({r.n_iter})")
    if tol:
        ax.axhline(tol, color=MUT, ls=":", lw=1, label="tolerancia")
    ax.set_xlabel("iteración k"); ax.set_ylabel("error relativo")
    ax.legend(fontsize=8); fig.tight_layout(); return fig


def curva_capacidad(s: md.ParametrosServidor, lam=None):
    lim = bl.limites(s)
    N = np.linspace(0.5, max(lim.n_pico * 2.5, 10), 500)
    fig, ax = _fig(7, 4)
    s0 = replace(s, termico=False)
    ax.plot(N, md.capacidad(N, s0), color=MUT, lw=1.2, ls="--", label="USL sin efecto térmico")
    ax.plot(N, md.capacidad(N, s), color=AZUL, lw=2, label="X_eff(N) con térmico" if s.termico else "X(N)")
    ax.plot(N, s.rho * md.capacidad(N, s), color=VERDE, lw=1.2, label=f"ρ·X_eff(N)  (ρ={s.rho:.0%})")
    ax.axvline(lim.n_pico, color=ROJO, ls=":", lw=1)
    ax.annotate(f"pico N={lim.n_pico:.1f}\nλ_máx={lim.lambda_max:,.0f}", (lim.n_pico, lim.lambda_max),
                xytext=(10, 18), textcoords="offset points", color=ROJO, fontsize=8)
    ax.plot(N, N * s.X1, color=LINEA, lw=1, label="Escalado lineal ideal")
    if lam:
        ax.axhline(lam, color=AMBAR, lw=1.2, label=f"λ = {lam:,.0f} req/s")
    ax.set_ylim(0, md.capacidad(lim.n_pico, s0) * 1.35)
    ax.set_xlabel("réplicas N"); ax.set_ylabel("req/s"); ax.legend(fontsize=8, loc="lower right")
    fig.tight_layout(); return fig


def convergencia_vs_lambda(s: md.ParametrosServidor, tol=1e-8):
    lim = bl.limites(s)
    lams = np.linspace(lim.lambda_max * 0.03, lim.lambda_max * 1.1, 120)
    it_pf, it_st, it_nw, dgs = [], [], [], []
    for lam in lams:
        rp = bl.resolver(lam, s, "Punto fijo", tol=tol, max_iter=500, lim=lim)
        ok = rp.convergio and rp.raiz <= lim.n_pico
        it_pf.append(rp.n_iter if ok else np.nan)
        rs = bl.resolver(lam, s, "Steffensen", tol=tol, lim=lim)
        it_st.append(rs.n_iter if rs.convergio and rs.raiz <= lim.n_pico else np.nan)
        rn = bl.resolver(lam, s, "Newton-Raphson", tol=tol, lim=lim)
        it_nw.append(rn.n_iter if rn.convergio and rn.raiz <= lim.n_pico else np.nan)
        dgs.append(float(md.dg(rp.raiz, lam, s)) if ok else np.nan)
    fig, axs = plt.subplots(1, 2, figsize=(10, 3.8), dpi=110)
    ax = axs[0]
    ax.plot(lams, dgs, color=AMBAR, lw=2)
    ax.axhline(1, color=ROJO, ls="--", lw=1); ax.axvline(lim.lambda_max, color=ROJO, ls=":", lw=1)
    ax.set_xlabel("λ (req/s)"); ax.set_ylabel("g′(N*)"); ax.set_title("Factor de contracción", fontsize=10)
    ax.set_ylim(0, 1.15)
    ax = axs[1]
    ax.plot(lams, it_pf, color=AMBAR, lw=1.8, label="Punto fijo")
    ax.plot(lams, it_st, color=VERDE, lw=1.5, label="Steffensen")
    ax.plot(lams, it_nw, color=AZUL, lw=1.5, label="Newton")
    ax.axvline(lim.lambda_max, color=ROJO, ls=":", lw=1, label="λ_máx")
    ax.set_yscale("log"); ax.set_xlabel("λ (req/s)"); ax.set_ylabel("iteraciones")
    ax.set_title("Costo computacional", fontsize=10); ax.legend(fontsize=8)
    fig.tight_layout(); return fig


def mapa_sensibilidad(s: md.ParametrosServidor, n=40, tol=1e-8):
    kappas = np.linspace(0.0001, 0.002, n)
    s0 = replace(s, kappa=float(kappas[0]))
    lam_hi = bl.limites(s0).lambda_max * 1.05
    lams = np.linspace(lam_hi * 0.03, lam_hi, n)
    Z = np.full((n, n), np.nan)
    for i, k in enumerate(kappas):
        sk = replace(s, kappa=float(k)); lim = bl.limites(sk)
        for j, lam in enumerate(lams):
            r = bl.resolver(lam, sk, "Punto fijo", tol=tol, max_iter=400, lim=lim)
            if r.convergio and r.raiz <= lim.n_pico:
                Z[i, j] = r.n_iter
    fig, ax = _fig(7, 4.3)
    cmap = plt.get_cmap("viridis").copy(); cmap.set_bad(ROJO, alpha=.35)
    im = ax.pcolormesh(lams, kappas, np.ma.masked_invalid(Z), cmap=cmap, shading="auto",
                       norm=matplotlib.colors.LogNorm(vmin=np.nanmin(Z), vmax=np.nanmax(Z)))
    cb = fig.colorbar(im, ax=ax); cb.set_label("iteraciones de punto fijo")
    ax.set_xlabel("λ (req/s)"); ax.set_ylabel("κ (coherencia)")
    ax.set_title("Zona roja: sin solución estable (|g′| ≥ 1)", fontsize=10)
    fig.tight_layout(); return fig
