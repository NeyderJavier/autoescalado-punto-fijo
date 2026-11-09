"""
Pruebas automáticas de la versión simple.

Cómo ejecutarlas (dentro de la carpeta version_simple):
    python -m pytest -v test_punto_fijo.py

Cada función que empieza con "test_" es una prueba: si todos los "assert"
se cumplen, la prueba PASA (PASSED); si alguno no, FALLA (FAILED).
"""
from punto_fijo import punto_fijo, recursos, solucion_exacta, trafico_maximo


def test_caso_normal():
    """600 req/s, servidores de 100 req/s → 9 servidores."""
    N, tabla, ok = punto_fijo(600, 100, 0.002)
    assert ok
    assert round(N, 4) == 8.4425
    assert recursos(N, 600, 100, 0.002)["servidores"] == 9


def test_coincide_con_formula_exacta():
    """Punto Fijo debe dar casi lo mismo que la fórmula cuadrática."""
    for trafico in [100, 300, 600, 850]:
        N, _, ok = punto_fijo(trafico, 100, 0.002, tol=1e-10)
        assert ok
        assert abs(N - solucion_exacta(trafico, 100, 0.002)) < 1e-6


def test_trafico_bajo():
    """Poco tráfico → pocos servidores y pocas iteraciones."""
    N, tabla, ok = punto_fijo(200, 100, 0.002)
    assert ok
    assert recursos(N, 200, 100, 0.002)["servidores"] == 3
    assert len(tabla) <= 5


def test_cerca_del_limite_necesita_mas_iteraciones():
    """Cerca del máximo el método converge, pero mucho más lento."""
    _, tabla_normal, _ = punto_fijo(600, 100, 0.002)
    _, tabla_limite, ok = punto_fijo(900, 100, 0.002)
    assert ok
    assert len(tabla_limite) > 5 * len(tabla_normal)


def test_saturado_no_tiene_solucion():
    """Por encima del máximo (≈915 req/s) el método debe decir que no hay solución."""
    _, maximo = trafico_maximo(100, 0.002)
    assert 914 < maximo < 916
    N, _, ok = punto_fijo(1000, 100, 0.002)
    assert not ok
    assert N is None
    assert solucion_exacta(1000, 100, 0.002) is None


def test_uso_real_cerca_del_80_por_ciento():
    """Al redondear hacia arriba, el uso real nunca pasa del 80 %."""
    for trafico in [150, 400, 600, 800]:
        N, _, ok = punto_fijo(trafico, 100, 0.002)
        uso = recursos(N, trafico, 100, 0.002)["uso"]
        assert 0.5 < uso <= 0.80


def test_tolerancia_mas_pequena_mas_iteraciones():
    """Pedir más precisión cuesta más iteraciones."""
    _, t3, _ = punto_fijo(600, 100, 0.002, tol=1e-3)
    _, t6, _ = punto_fijo(600, 100, 0.002, tol=1e-6)
    _, t8, _ = punto_fijo(600, 100, 0.002, tol=1e-8)
    assert len(t3) < len(t6) < len(t8)
