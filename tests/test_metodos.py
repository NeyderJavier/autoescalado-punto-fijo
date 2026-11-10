"""
Pruebas automáticas.      python -m pytest -v

Cada prueba tiene una razón matemática: si la teoría dice que un método es
exacto para cierto tipo de función, el programa debe dar el valor exacto.
"""
import math
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from metodos import simpson_13, simpson_38, trapecio  # noqa: E402
from problemas import TODOS  # noqa: E402


# ---------------------------------------------------------------- Trapecio
def test_trapecio_es_exacto_con_rectas():
    """Una recta se aproxima perfecto con trapecios: ∫(2x+1) de 0 a 4 = 20."""
    assert trapecio.integrar(lambda x: 2 * x + 1, 0, 4, 1) == pytest.approx(20)


def test_trapecio_ejemplo_del_cuaderno():
    """∫x² de 0 a 2 con n = 2:  h/2·[f(0) + 2f(1) + f(2)] = 0.5·(0 + 2 + 4) = 3."""
    assert trapecio.integrar(lambda x: x**2, 0, 2, 2) == pytest.approx(3)


def test_trapecio_coeficientes():
    assert trapecio.coeficientes(4) == [1, 2, 2, 2, 1]


def test_trapecio_error_baja_4_veces_al_duplicar_n():
    """El error del trapecio es proporcional a h²: n×2 ⇒ error ÷4."""
    f, exacta = math.exp, math.e - 1
    e1 = abs(trapecio.integrar(f, 0, 1, 10) - exacta)
    e2 = abs(trapecio.integrar(f, 0, 1, 20) - exacta)
    assert e1 / e2 == pytest.approx(4, rel=0.01)


# ---------------------------------------------------------------- Simpson 1/3
def test_simpson13_es_exacto_con_cubicas():
    """Simpson 1/3 es exacto hasta grado 3: ∫x³ de 0 a 2 = 4 (con solo n = 2)."""
    assert simpson_13.integrar(lambda x: x**3, 0, 2, 2) == pytest.approx(4)


def test_simpson13_ejemplo_del_cuaderno():
    """∫x² de 0 a 2 con n = 2:  h/3·[f(0) + 4f(1) + f(2)] = (1/3)·(0 + 4 + 4) = 8/3."""
    assert simpson_13.integrar(lambda x: x**2, 0, 2, 2) == pytest.approx(8 / 3)


def test_simpson13_coeficientes():
    assert simpson_13.coeficientes(6) == [1, 4, 2, 4, 2, 4, 1]


def test_simpson13_rechaza_n_impar():
    with pytest.raises(ValueError):
        simpson_13.integrar(lambda x: x, 0, 1, 3)


def test_simpson13_error_baja_16_veces_al_duplicar_n():
    """El error de Simpson es proporcional a h⁴: n×2 ⇒ error ÷16."""
    f, exacta = math.exp, math.e - 1
    e1 = abs(simpson_13.integrar(f, 0, 1, 4) - exacta)
    e2 = abs(simpson_13.integrar(f, 0, 1, 8) - exacta)
    assert e1 / e2 == pytest.approx(16, rel=0.02)


# ---------------------------------------------------------------- Simpson 3/8
def test_simpson38_es_exacto_con_cubicas():
    """Simpson 3/8 también es exacto hasta grado 3: ∫(x³ − 2x + 5) de 1 a 4 = 63.75 − 15 + 15."""
    assert simpson_38.integrar(lambda x: x**3 - 2 * x + 5, 1, 4, 3) == pytest.approx(63.75)


def test_simpson38_coeficientes():
    assert simpson_38.coeficientes(6) == [1, 3, 3, 2, 3, 3, 1]


def test_simpson38_rechaza_n_no_multiplo_de_3():
    with pytest.raises(ValueError):
        simpson_38.integrar(lambda x: x, 0, 1, 4)


def test_simpson38_error_baja_16_veces_al_duplicar_n():
    f, exacta = math.exp, math.e - 1
    e1 = abs(simpson_38.integrar(f, 0, 1, 6) - exacta)
    e2 = abs(simpson_38.integrar(f, 0, 1, 12) - exacta)
    assert e1 / e2 == pytest.approx(16, rel=0.02)


# ---------------------------------------------------------------- Generales
@pytest.mark.parametrize("metodo", [trapecio, simpson_13, simpson_38])
def test_paso_a_paso_da_lo_mismo_que_integrar(metodo):
    f = lambda x: math.sin(x) + x**2
    _, _, _, resultado = metodo.paso_a_paso(f, 0, 3, 6)
    assert resultado == pytest.approx(metodo.integrar(f, 0, 3, 6))


@pytest.mark.parametrize("problema", TODOS, ids=lambda p: p.titulo[:25])
def test_todos_convergen_al_valor_exacto(problema):
    """Con muchos subintervalos, los tres métodos se acercan al valor exacto."""
    for metodo, tolerancia in [(trapecio, 1e-3), (simpson_13, 1e-7), (simpson_38, 1e-7)]:
        aprox = metodo.integrar(problema.f, problema.a, problema.b, 600)
        assert abs(aprox - problema.exacta) / problema.exacta < tolerancia


def test_simpson_mejor_que_trapecio_en_los_problemas():
    """Con el mismo n, Simpson 1/3 tiene menos error que el trapecio."""
    for p in TODOS:
        e_t = abs(trapecio.integrar(p.f, p.a, p.b, 6) - p.exacta)
        e_s = abs(simpson_13.integrar(p.f, p.a, p.b, 6) - p.exacta)
        assert e_s <= e_t
