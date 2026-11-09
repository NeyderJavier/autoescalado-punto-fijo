"""Une el modelo del clúster con los métodos numéricos."""
from __future__ import annotations

import math
from dataclasses import dataclass

from . import metodos as m
from . import modelo as md

METODOS = ["Punto fijo", "Steffensen", "Newton-Raphson", "Secante", "Bisección"]
ORDEN_TEORICO = {"Punto fijo": "1 (lineal)", "Steffensen": "2 (cuadrático)",
                 "Newton-Raphson": "2 (cuadrático)", "Secante": "1.618 (superlineal)",
                 "Bisección": "1 (lineal, razón ½)"}


@dataclass
class Limites:
    n_pico: float          # réplicas donde la capacidad es máxima
    lambda_max: float      # tráfico máximo sostenible al ρ objetivo
    iter_dorada: int


def limites(s: md.ParametrosServidor, n_max_busqueda: float = 5000.0) -> Limites:
    """Pico de X_eff(N) por sección dorada (incluye el efecto térmico)."""
    n_pico, k = m.seccion_dorada_max(lambda n: float(md.capacidad(n, s)), 0.5, n_max_busqueda)
    return Limites(n_pico, md.lambda_maximo(s, n_pico), k)


def resolver(lam: float, s: md.ParametrosServidor, metodo: str = "Punto fijo",
             x0: float | None = None, tol: float = 1e-8, max_iter: int = 200,
             lim: Limites | None = None) -> m.Resultado:
    x0 = md.n_inicial(lam, s) if x0 is None else x0
    g = lambda n: float(md.g(n, lam, s))
    F = lambda n: float(md.F(n, lam, s))
    dF = lambda n: float(md.dF(n, lam, s))

    if metodo == "Punto fijo":
        return m.punto_fijo(g, x0, tol, max_iter)
    if metodo == "Steffensen":
        return m.steffensen(g, x0, tol, max_iter)
    if metodo == "Newton-Raphson":
        return m.newton(F, dF, x0, tol, max_iter)
    if metodo == "Secante":
        return m.secante(F, x0, x0 * 1.1 + 0.5, tol, max_iter)
    if metodo == "Bisección":
        lim = lim or limites(s)
        # Raíz "buena": entre casi 0 y el pico de capacidad
        return m.biseccion(F, 1e-6, lim.n_pico, tol, max_iter)
    raise ValueError(metodo)


def comparar(lam: float, s: md.ParametrosServidor, tol: float = 1e-8,
             max_iter: int = 200, x0: float | None = None) -> list[tuple[m.Resultado, float]]:
    """Ejecuta los 5 métodos. Devuelve [(resultado, orden_estimado)]."""
    lim = limites(s)
    salida = []
    referencia = None
    for nombre in METODOS:
        r = resolver(lam, s, nombre, x0=x0, tol=tol, max_iter=max_iter, lim=lim)
        salida.append(r)
        if nombre == "Bisección" and r.convergio:
            referencia = r.raiz
    # Raíz de referencia muy precisa para estimar órdenes
    ref = resolver(lam, s, "Newton-Raphson", tol=1e-15, max_iter=200, x0=x0)
    xr = ref.raiz if ref.convergio else referencia
    # La bisección no tiene error monótono: su orden experimental no es significativo
    return [(r, m.orden_convergencia(r, xr) if (r.convergio and xr and r.metodo != "Bisección")
             else math.nan) for r in salida]
