"""
Configuration management for Snakeer package manager
Handles project_packages.json read/write and dependency management
"""

import os
import json
from typing import Dict, Optional, Any
from .utils import load_json, save_json


class Config:
    """Manages project_packages.json configuration"""
    
    DEFAULT_CONFIG: Dict[str, Any] = {
        "name": "my_project",
        "version": "1.0.0",
        "snakeer_dependencies": {},
        "installed_dependencies_versions": {}
    }
    
    def __init__(self, project_path: Optional[str] = None):
        self.project_path = project_path or os.getcwd()
        self.config_path = os.path.join(self.project_path, "project_packages.json")
        self._config: Optional[Dict[str, Any]] = None

    
    def _load(self) -> dict:
        """Load configuration from file or create default"""
        if self._config is not None:
            return self._config
            
        if os.path.exists(self.config_path):
            try:
                self._config = load_json(self.config_path)
                # Ensure all required fields exist
                for key, value in self.DEFAULT_CONFIG.items():
                    if key not in self._config:
                        self._config[key] = value
                return self._config
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load config, using defaults: {e}")
                self._config = self.DEFAULT_CONFIG.copy()
                return self._config
        else:
            self._config = self.DEFAULT_CONFIG.copy()
            self._save()
            return self._config
    
    def _save(self):
        """Save configuration to file"""
        if self._config is None:
            self._load()
        if self._config is not None:
            save_json(self.config_path, self._config)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        config = self._load()
        return config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set configuration value"""
        config = self._load()
        config[key] = value
        self._save()
    
    # Dependency management
    
    def get_dependencies(self) -> Dict[str, str]:
        """Get all requested dependencies with version specs"""
        return self._load().get("snakeer_dependencies", {})
    
    def get_installed_versions(self) -> Dict[str, str]:
        """Get all installed dependency versions"""
        return self._load().get("installed_dependencies_versions", {})
    
    def add_dependency(self, name: str, version_spec: str):
        """Add a dependency to the project"""
        config = self._load()
        config["snakeer_dependencies"][name] = version_spec
        self._save()
        print(f"Added {name}@{version_spec} to dependencies")
    
    def remove_dependency(self, name: str):
        """Remove a dependency from the project"""
        config = self._load()
        if name in config["snakeer_dependencies"]:
            del config["snakeer_dependencies"][name]
        if name in config["installed_dependencies_versions"]:
            del config["installed_dependencies_versions"][name]
        self._save()
        print(f"Removed {name} from dependencies")
    
    def set_installed_version(self, name: str, version: str):
        """Set the installed version of a package"""
        config = self._load()
        config["installed_dependencies_versions"][name] = version
        self._save()
    
    def get_requested_version(self, name: str) -> Optional[str]:
        """Get the requested version specification for a package"""
        return self.get_dependencies().get(name)
    
    def get_installed_package(self, name: str) -> Optional[str]:
        """Get the installed version of a package"""
        return self.get_installed_versions().get(name)
    
    def get_config_path(self) -> str:
        """Get the configuration file path"""
        return self.config_path
    
    def is_installed(self, name: str, version: Optional[str] = None) -> bool:
        """Check if a package is installed (optionally check specific version)"""
        installed = self.get_installed_package(name)
        if installed is None:
            return False
        if version is None:
            return True
        return installed == version
    
    def get_project_name(self) -> str:
        """Get project name"""
        return self._load().get("name", "unknown")
    
    def get_project_version(self) -> str:
        """Get project version"""
        return self._load().get("version", "0.0.0")
    
    def get_installed_packages(self) -> Dict[str, str]:
        """Get dictionary of installed packages"""
        return self.get_installed_versions()
