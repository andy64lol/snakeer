"""
Module loader for Snakeer
Provides require() function for loading packages from snakeer_modules
"""

import os
import sys
import importlib.util
from typing import Any, Optional
from .utils import get_modules_path


def require(name: str) -> Any:
    """
    Load a module from snakeer_modules directory (Node.js-style require)
    
    Args:
        name: Package name to load
        
    Returns:
        The loaded module
        
    Raises:
        ImportError: If the package cannot be found or loaded
    """
    modules_dir = get_modules_path()
    package_dir = os.path.join(modules_dir, name)
    
    # Check if package exists
    if not os.path.exists(package_dir):
        raise ImportError(f"Package '{name}' not found in snakeer_modules. Run 'snakeer install' first.")
    
    # Look for index.py (main entry point)
    index_path = os.path.join(package_dir, "index.py")
    
    # Alternative: look for package_name.py
    if not os.path.exists(index_path):
        alt_path = os.path.join(package_dir, f"{name}.py")
        if os.path.exists(alt_path):
            index_path = alt_path
        else:
            # Try to find any .py file
            py_files = [f for f in os.listdir(package_dir) if f.endswith('.py') and f != 'metadata.json']
            if py_files:
                index_path = os.path.join(package_dir, py_files[0])
            else:
                raise ImportError(f"No Python module found in package '{name}'")
    
    # Load the module
    spec = importlib.util.spec_from_file_location(name, index_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module spec for '{name}'")
    
    module = importlib.util.module_from_spec(spec)
    
    # Add to sys.modules to avoid reloading
    sys.modules[name] = module
    
    # Execute the module
    spec.loader.exec_module(module)
    
    return module


def require_all() -> dict:
    """
    Load all installed packages from snakeer_modules
    
    Returns:
        Dictionary mapping package names to loaded modules
    """
    modules_dir = get_modules_path()
    loaded = {}
    
    if not os.path.exists(modules_dir):
        return loaded
    
    for name in os.listdir(modules_dir):
        package_dir = os.path.join(modules_dir, name)
        if os.path.isdir(package_dir):
            try:
                loaded[name] = require(name)
            except ImportError as e:
                print(f"Warning: Could not load {name}: {e}")
    
    return loaded


def reload(name: str) -> Any:
    """
    Reload a previously loaded module
    
    Args:
        name: Package name to reload
        
    Returns:
        The reloaded module
    """
    # Remove from sys.modules if present
    if name in sys.modules:
        del sys.modules[name]
    
    return require(name)
