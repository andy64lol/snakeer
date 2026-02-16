"""
Package installer for Snakeer
Handles downloading, extracting, and installing packages from GitHub registry
"""

import os
import json
import zipfile
import tarfile
import shutil
import base64
import requests
from typing import Dict, List, Optional, Tuple
from .config import Config
from .utils import (
    download_file, ensure_dir, get_cache_path, get_modules_path,
    find_best_version, version_satisfies, load_json, save_json,
    calculate_hash
)


class Installer:
    """Handles package installation from GitHub registry"""
    
    GITHUB_API_BASE = "https://api.github.com"
    REGISTRY_REPO = "andy64lol/snakeer_packages_lib"
    
    def __init__(self, config: Config):
        self.config = config
        self.cache_dir = get_cache_path()
        self.modules_dir = get_modules_path()
        self.github_token = os.environ.get("GITHUB_TOKEN", "")
        ensure_dir(self.cache_dir)
        ensure_dir(self.modules_dir)
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for GitHub API requests"""
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Snakeer-Package-Manager"
        }
        if self.github_token:
            headers["Authorization"] = f"token {self.github_token}"
        return headers
    
    def _get_registry_contents(self, path: str = "") -> List[Dict]:
        """Get contents from GitHub repository"""
        url = f"{self.GITHUB_API_BASE}/repos/{self.REGISTRY_REPO}/contents/{path}"
        try:
            response = requests.get(url, headers=self._get_headers(), timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error accessing registry: {e}")
            return []
    
    def _get_package_versions(self, package_name: str) -> List[str]:
        """Get available versions for a package"""
        contents = self._get_registry_contents(f"packages/{package_name}")
        versions = []
        for item in contents:
            if item["type"] == "dir":
                # Directory name is the version
                versions.append(item["name"])
        return versions
    
    def _download_package(self, package_name: str, version: str) -> Optional[str]:
        """
        Download package from GitHub registry
        Returns path to downloaded file or None if failed
        """
        package_path = f"packages/{package_name}/{version}"
        contents = self._get_registry_contents(package_path)
        
        # Look for package archive
        archive_item = None
        for item in contents:
            if item["name"].endswith((".zip", ".tar.gz")):
                archive_item = item
                break
        
        if not archive_item:
            print(f"No package archive found for {package_name}@{version}")
            return None
        
        # Download the file
        download_url = archive_item["download_url"]
        archive_name = archive_item["name"]
        cache_file = os.path.join(self.cache_dir, f"{package_name}-{version}-{archive_name}")
        
        print(f"Downloading {package_name}@{version}...")
        if download_file(download_url, cache_file):
            return cache_file
        
        return None
    
    def _extract_package(self, archive_path: str, package_name: str, version: str) -> bool:
        """Extract package archive to snakeer_modules"""
        package_dir = os.path.join(self.modules_dir, package_name)
        
        # Remove existing installation
        if os.path.exists(package_dir):
            shutil.rmtree(package_dir)
        
        ensure_dir(package_dir)
        
        try:
            if archive_path.endswith(".zip"):
                with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                    zip_ref.extractall(package_dir)
            elif archive_path.endswith(".tar.gz"):
                with tarfile.open(archive_path, 'r:gz') as tar_ref:
                    tar_ref.extractall(package_dir)
            
            # Move contents from subdirectory if extracted into one
            items = os.listdir(package_dir)
            if len(items) == 1 and os.path.isdir(os.path.join(package_dir, items[0])):
                subdir = os.path.join(package_dir, items[0])
                for item in os.listdir(subdir):
                    shutil.move(os.path.join(subdir, item), package_dir)
                os.rmdir(subdir)
            
            return True
        except Exception as e:
            print(f"Error extracting package: {e}")
            return False
    
    def _read_package_metadata(self, package_name: str) -> Optional[Dict]:
        """Read metadata.json from installed package"""
        metadata_path = os.path.join(self.modules_dir, package_name, "metadata.json")
        if os.path.exists(metadata_path):
            try:
                return load_json(metadata_path)
            except (json.JSONDecodeError, IOError):
                pass
        return None
    
    def _install_dependencies(self, package_name: str, installed: Optional[List[str]] = None):
        """Recursively install package dependencies"""
        if installed is None:
            installed = []
        
        if package_name in installed:
            return  # Avoid circular dependencies
        
        installed.append(package_name)
        
        metadata = self._read_package_metadata(package_name)
        if metadata and "dependencies" in metadata:
            deps = metadata["dependencies"]
            print(f"Installing dependencies for {package_name}: {list(deps.keys())}")
            
            for dep_name, dep_spec in deps.items():
                if not self.config.is_installed(dep_name):
                    self.install_package(dep_name, dep_spec)
    
    def install_package(self, name: str, version_spec: str = "latest") -> bool:
        """
        Install a single package
        """
        # Check if already installed with correct version
        if self.config.is_installed(name):
            installed_version = self.config.get_installed_package(name)
            if installed_version and (version_spec == "latest" or version_satisfies(installed_version, version_spec)):
                print(f"{name}@{installed_version} already installed")
                return True
        
        # Find best matching version
        available_versions = self._get_package_versions(name)
        if not available_versions:
            print(f"Package {name} not found in registry")
            return False
        
        if version_spec == "latest":
            version = available_versions[0]  # Assuming sorted
        else:
            version = find_best_version(available_versions, version_spec)
        
        if not version:
            print(f"No version found for {name} matching {version_spec}")
            return False
        
        # Download and extract
        archive_path = self._download_package(name, version)
        if not archive_path:
            return False
        
        if not self._extract_package(archive_path, name, version):
            return False
        
        # Update config
        self.config.set_installed_version(name, version)
        
        # Install dependencies
        self._install_dependencies(name)
        
        print(f"✅ Installed {name}@{version}")
        return True
    
    def install_all(self, force: bool = False):
        """Install all dependencies from project_packages.json"""
        dependencies = self.config.get_dependencies()
        
        if not dependencies:
            print("No dependencies to install")
            return
        
        print(f"Found {len(dependencies)} dependencies")
        
        for name, version_spec in dependencies.items():
            if force or not self.config.is_installed(name):
                self.install_package(name, version_spec)
            else:
                installed_version = self.config.get_installed_package(name)
                print(f"{name}@{installed_version} already installed (use --force to reinstall)")
    
    def remove_package(self, name: str):
        """Remove an installed package"""
        package_dir = os.path.join(self.modules_dir, name)
        if os.path.exists(package_dir):
            shutil.rmtree(package_dir)
            print(f"Removed {name} from snakeer_modules")
    
    def update_package(self, name: str):
        """Update a package to latest matching version"""
        version_spec = self.config.get_requested_version(name)
        if not version_spec:
            print(f"{name} is not in dependencies")
            return
        
        # Force reinstall
        self.remove_package(name)
        self.install_package(name, version_spec)
    
    def update_all(self):
        """Update all packages"""
        dependencies = self.config.get_dependencies()
        for name, version_spec in dependencies.items():
            self.update_package(name)
    
    def publish(self, registry_url: Optional[str] = None):
        """
        Publish current package to registry
        This creates a package archive and uploads it to GitHub
        """
        project_name = self.config.get_project_name()
        project_version = self.config.get_project_version()
        
        # Create package archive
        package_dir = os.getcwd()
        archive_name = f"{project_name}-{project_version}.zip"
        archive_path = os.path.join(self.cache_dir, archive_name)
        
        # Create zip excluding certain directories
        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(package_dir):
                # Exclude directories
                dirs[:] = [d for d in dirs if d not in [
                    '.git', '.snakeer_cache', 'snakeer_modules', 
                    '__pycache__', '.venv', 'venv', 'node_modules'
                ]]
                
                for file in files:
                    if file.endswith(('.pyc', '.pyo', '.pyd')):
                        continue
                    
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, package_dir)
                    zipf.write(file_path, arcname)
        
        print(f"Created package archive: {archive_path}")
        print(f"To publish, manually upload to: https://github.com/{self.REGISTRY_REPO}/tree/main/packages/{project_name}/{project_version}")
        print("Or use the serverless upload function with your GitHub token")
        
        return archive_path
