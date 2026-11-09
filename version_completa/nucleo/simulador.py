"""
Simulación minuto a minuto del autoescalador.

Realismo agregado:
  - Arranque en frío: una réplica nueva tarda `arranque_min` minutos en atender.
  - Cooldown: no se reducen réplicas hasta `cooldown_min` después del último cambio
    (evita el "flapping").
  - Estrategia reactiva (usa λ actual) o predictiva (usa λ pronosticado por
    mínimos cuadrados para cuando la réplica esté lista).
  - Warm start: el N* del minuto anterior es la semilla del método → menos iteraciones.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
import pandas as pd

from . import balance as bl
from . import modelo as md
from .prediccion import pronosticar


@dataclass
class ConfigSimulacion:
    minutos: int = 180
    estrategia: str = "reactiva"     # "reactiva" | "predictiva"
    metodo: str = "Punto fijo"
    tol: float = 1e-8
    max_iter: int = 200
    warm_start: bool = True
    arranque_min: int = 3
    cooldown_min: int = 5
    ventana: int = 15
    margen: float = 0.05             # margen de seguridad sobre el pronóstico
    min_replicas: int = 1
    max_replicas: int = 0            # 0 = sin cuota
    umbral_sla: float = 0.95         # U por encima de esto = violación de SLA


def simular(lam_serie: np.ndarray, s: md.ParametrosServidor,
            c: ConfigSimulacion) -> pd.DataFrame:
    lim = bl.limites(s)
    filas = []
    n_prev = None
    activas = 0
    pendientes: list[list[int]] = []   # [minuto_listo, cantidad]
    ultimo_cambio = -10**9

    for t in range(c.minutos):
        lam = float(lam_serie[t])

        # 1) ¿Cuánto tráfico planificar?
        if c.estrategia == "predictiva" and t >= 3:
            ini = max(0, t - c.ventana + 1)
            lam_plan, modelo_pred = pronosticar(np.arange(ini, t + 1, dtype=float),
                                                lam_serie[ini:t + 1], c.arranque_min)
            lam_plan = max(lam_plan, lam) * (1 + c.margen)
        else:
            lam_plan, modelo_pred = lam, "—"

        # 2) Resolver la ecuación de balance
        x0 = n_prev if (c.warm_start and n_prev) else None
        res = bl.resolver(lam_plan, s, c.metodo, x0=x0, tol=c.tol, max_iter=c.max_iter, lim=lim)
        it_frio = res.n_iter
        if c.warm_start and x0 is not None:
            it_frio = bl.resolver(lam_plan, s, c.metodo, x0=None, tol=c.tol,
                                  max_iter=c.max_iter, lim=lim).n_iter
        saturado = not res.convergio or res.raiz > lim.n_pico
        if saturado:
            n_star = math.nan
            deseadas = max(c.min_replicas, int(round(lim.n_pico)))
            n_prev = None
        else:
            n_star = res.raiz
            deseadas = max(c.min_replicas, math.ceil(n_star - 1e-9))
            n_prev = n_star
        if c.max_replicas:
            deseadas = min(deseadas, c.max_replicas)

        # 3) Aplicar decisión (arranque en frío + cooldown)
        if t == 0:
            activas = deseadas
            ultimo_cambio = 0
        else:
            for p in pendientes:
                if p[0] <= t:
                    activas += p[1]
            pendientes = [p for p in pendientes if p[0] > t]
            objetivo = activas + sum(p[1] for p in pendientes)
            if deseadas > objetivo:
                pendientes.append([t + c.arranque_min, deseadas - objetivo])
                ultimo_cambio = t
            elif deseadas < objetivo and t - ultimo_cambio >= c.cooldown_min:
                quitar = objetivo - deseadas
                while quitar and pendientes:
                    q = min(quitar, pendientes[-1][1])
                    pendientes[-1][1] -= q; quitar -= q
                    if pendientes[-1][1] == 0:
                        pendientes.pop()
                activas -= quitar
                ultimo_cambio = t
        en_arranque = sum(p[1] for p in pendientes)

        # 4) Métricas del minuto
        r = md.recursos(max(activas, 1), lam, s)
        cap = float(md.capacidad(max(activas, 1), s))
        facturadas = activas + en_arranque
        costo_min = (facturadas * s.vcpu_por_replica * s.costo_vcpu_h + r.ram_gb * s.costo_gb_h) / 60

        filas.append({
            "minuto": t, "lambda": lam, "lambda_plan": lam_plan, "modelo_pred": modelo_pred,
            "n_star": n_star, "deseadas": deseadas, "activas": activas, "en_arranque": en_arranque,
            "capacidad": cap, "capacidad_obj": s.rho * cap,
            "utilizacion": r.utilizacion, "temperatura": r.temperatura,
            "vcpu": facturadas * s.vcpu_por_replica, "ram_gb": r.ram_gb,
            "iteraciones": res.n_iter, "iter_sin_warm": it_frio,
            "error_final": res.error_final, "convergio": res.convergio, "saturado": saturado,
            "perdidas": max(0.0, lam - cap) * 60, "violacion_sla": r.utilizacion > c.umbral_sla,
            "costo_usd": costo_min,
            "dg": float(md.dg(n_star, lam_plan, s)) if not saturado else math.nan,
        })
    return pd.DataFrame(filas)


def resumen(df: pd.DataFrame) -> dict:
    total = df["lambda"].sum() * 60
    return {
        "Costo total (USD)": df["costo_usd"].sum(),
        "Peticiones perdidas": df["perdidas"].sum(),
        "% peticiones perdidas": 100 * df["perdidas"].sum() / total if total else 0.0,
        "Minutos con violación SLA": int(df["violacion_sla"].sum()),
        "Minutos saturado": int(df["saturado"].sum()),
        "Utilización promedio (%)": 100 * df["utilizacion"].clip(upper=1.5).mean(),
        "Iteraciones promedio": df["iteraciones"].mean(),
        "Iteraciones promedio sin warm start": df["iter_sin_warm"].mean(),
        "Réplicas máximas": int(df["activas"].max()),
        "Temperatura máxima (°C)": df["temperatura"].max(),
    }
