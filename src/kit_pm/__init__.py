"""
Kit - HumoticaOS Package Manager & AI Security Gateway

De Rechter van het Systeem - validates packages against JIS/SNAFT
before allowing them into your system.

One Love, One fAmIly!
"""

__version__ = "0.1.1"
__author__ = "HumoticaOS Team"

from .core import PackageRegistry, KitValidator
from .cli import main

__all__ = ["PackageRegistry", "KitValidator", "main", "__version__"]
