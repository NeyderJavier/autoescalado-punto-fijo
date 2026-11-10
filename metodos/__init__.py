"""Los tres métodos de integración numérica, uno por archivo."""
from . import simpson_13, simpson_38, trapecio

TODOS = [trapecio, simpson_13, simpson_38]
