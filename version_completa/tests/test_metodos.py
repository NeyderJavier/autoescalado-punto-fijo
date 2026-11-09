"""
Pruebas automáticas:  python -m pytest -v
Se validan los métodos propios contra scipy.optimize.brentq (referencia).
"""
import math
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from nucleo import balance as bl  # noqa: E402
from nucleo import metodos as m  # noqa: E402
from nucleo import modelo as md  # noqa: E402
from nucleo.prediccion import _gauss, pronosticar  # noqa: E402

S = md.ParametrosServidor()
S_SIN_TERMICO = md.ParametrosServidor(termico=False)


@pytest.mark.parametrize("s", [S, S_SIN_TERMICO])
@pytest.mark.parametrize("frac", [0.1, 0.4, 0.7, 0.95])
@pytest.mark.parametrize("metodo", bl.METODOS)
def test_raiz_coincide_con_scipy(s, frac, metodo):
    from scipy.optimize import brentq
    lim = bl.limites(s)
    lam = frac * lim.lambda_max
    ref = brentq(lambda n: md.F(n, lam, s), 1e-6, lim.n_pico, xtol=1e-14)
    r = bl.resolver(lam, s, metodo, tol=1e-10, max_iter=1000, lim=lim)
    assert r.convergio
    assert abs(r.raiz - ref) / ref < 1e-6


def test_balance_se_cumple():
    lam = 800
    r = bl.resolver(lam, S, "Punto fijo", tol=1e-12, max_iter=1000)
    assert math.isclose(S.rho * md.capacidad(r.raiz, S), lam, rel_tol=1e-9)


def test_punto_fijo_diverge_sobre_lambda_max():
    lim = bl.limites(S)
    r = bl.resolver(lim.lambda_max * 1.05, S, "Punto fijo", max_iter=2000)
    assert not r.convergio


def test_derivadas_analiticas():
    h = 1e-6
    for N in [2.0, 15.0, 40.0]:
        num_g = (md.g(N + h, 900, S) - md.g(N - h, 900, S)) / (2 * h)
        num_F = (md.F(N + h, 900, S) - md.F(N - h, 900, S)) / (2 * h)
        assert math.isclose(md.dg(N, 900, S), num_g, rel_tol=1e-5)
        assert math.isclose(md.dF(N, 900, S), num_F, rel_tol=1e-5)


def test_pico_usl_analitico():
    lim = bl.limites(S_SIN_TERMICO)
    assert math.isclose(lim.n_pico, md.n_pico_analitico(S_SIN_TERMICO), rel_tol=1e-5)


def test_criterio_convergencia():
    """En la solución estable siempre |g'(N*)| < 1."""
    lim = bl.limites(S)
    for frac in np.linspace(0.05, 0.99, 15):
        lam = frac * lim.lambda_max
        r = bl.resolver(lam, S, "Newton-Raphson", tol=1e-12)
        assert abs(md.dg(r.raiz, lam, S)) < 1


def test_ordenes_de_convergencia():
    lam = 0.8 * bl.limites(S).lambda_max
    ordenes = {r.metodo: p for r, p in bl.comparar(lam, S, tol=1e-13)}
    assert abs(ordenes["Punto fijo"] - 1) < 0.1
    assert ordenes["Newton-Raphson"] > 1.7
    assert ordenes["Steffensen"] > 1.7
    assert 1.4 < ordenes["Secante"] < 2.0


def test_seccion_dorada():
    x, _ = m.seccion_dorada_max(lambda x: -(x - 3.7) ** 2, 0, 10)
    assert abs(x - 3.7) < 1e-5


def test_gauss():
    A = np.array([[4.0, 1, 2], [1, 5, 1], [2, 1, 6]])
    y = np.array([1.0, 2, 3])
    assert np.allclose(_gauss(A, y), np.linalg.solve(A, y))


def test_pronostico_exponencial():
    t = np.arange(15, dtype=float)
    lam = 100 * np.exp(0.05 * t)
    valor, modelo = pronosticar(t, lam, 3)
    assert modelo == "exponencial"
    assert math.isclose(valor, 100 * np.exp(0.05 * 17), rel_tol=1e-6)
