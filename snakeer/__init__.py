"""
Snakeer - A Node.js-style package manager for Python
"""

__version__ = "1.0.0"
__author__ = "andy64lol"

from .loader import require
from .config import Config
from .installer import Installer

__all__ = ['require', 'Config', 'Installer']
