"""Общий пакет лабораторных 3 и 4 (PEP 420 path extension)."""
from pkgutil import extend_path

__path__ = extend_path(__path__, __name__)
