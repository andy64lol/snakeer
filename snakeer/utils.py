"""
Utility functions for Snakeer package manager
"""

import re
import os
import json
import hashlib
import requests
from typing import Dict, Tuple, Optional

def parse_version_spec(spec: str) -> Tuple[str, str]:
    """
    Parse version specification like >=1.0.0, ^1.0.0, ~1.0.0, or 1.0.0
    Returns (operator, version)
    """
    spec = spec.strip()
    
    # Check for operators
    if spec.startswith(">="):
        return (">=", spec[2:])
    elif spec.startswith("^"):
        return ("^", spec[1:])
    elif spec.startswith("~"):
        return ("~", spec[1:])
    elif spec == "latest":
        return ("latest", "")
    else:
        # No operator, exact version
        return ("=", spec)

def version_satisfies(version: str, spec: str) -> bool:
    """
    Check if a version satisfies a specification
    """
    op, spec_version = parse_version_spec(spec)
    
    if op == "latest":
        return True
    
    if op == "=":
        return version == spec_version
    
    # Parse versions
    v_parts = [int(x) for x in version.split(".")]
    sv_parts = [int(x) for x in spec_version.split(".")]
    
    # Pad with zeros
    while len(v_parts) < 3:
        v_parts.append(0)
    while len(sv_parts) < 3:
        sv_parts.append(0)
    
    if op == ">=":
        return v_parts >= sv_parts
    
    elif op == "^":
        # Compatible with version (major version must match, minor/patch can be higher)
        return v_parts[0] == sv_parts[0] and v_parts >= sv_parts
    
    elif op == "~":
        # Approximately equivalent to version (major.minor must match)
        return v_parts[0] == sv_parts[0] and v_parts[1] == sv_parts[1] and v_parts >= sv_parts
    
    return False

def find_best_version(available_versions: list, spec: str) -> Optional[str]:
    """
    Find the best version that satisfies the specification
    """
    op, spec_version = parse_version_spec(spec)
    
    # Sort versions (higher first)
    def version_key(v):
        parts = [int(x) for x in v.split(".")]
        while len(parts) < 3:
            parts.append(0)
        return tuple(parts)
    
    sorted_versions = sorted(available_versions, key=version_key, reverse=True)
    
    for version in sorted_versions:
        if version_satisfies(version, spec):
            return version
    
    return None

def download_file(url: str, dest_path: str, chunk_size: int = 8192) -> bool:
    """
    Download a file from URL to destination path
    """
    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        
        with open(dest_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
        
        return True
    except Exception as e:
        print(f"Download error: {e}")
        return False

def calculate_hash(filepath: str) -> str:
    """
    Calculate MD5 hash of a file
    """
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def load_json(filepath: str) -> dict:
    """Load JSON file"""
    with open(filepath, 'r') as f:
        return json.load(f)

def save_json(filepath: str, data: dict):
    """Save data to JSON file"""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

def ensure_dir(path: str):
    """Ensure directory exists"""
    os.makedirs(path, exist_ok=True)

def get_cache_path() -> str:
    """Get cache directory path"""
    return os.path.join(os.getcwd(), ".snakeer_cache")

def get_modules_path() -> str:
    """Get modules directory path"""
    return os.path.join(os.getcwd(), "snakeer_modules")

def get_project_config_path() -> str:
    """Get project_packages.json path"""
    return os.path.join(os.getcwd(), "project_packages.json")
