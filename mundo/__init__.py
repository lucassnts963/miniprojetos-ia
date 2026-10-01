"""Mundo simulado 2D, reaproveitável pelos miniprojetos (ver README.md nesta pasta)."""
from .mundo import Mundo
from .objetos import Bolas, Carros
from .pistas import PISTAS, Pista

__all__ = ["Mundo", "Carros", "Bolas", "Pista", "PISTAS"]
