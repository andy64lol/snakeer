#!/usr/bin/env python3
"""
Snakeer CLI - Command line interface for the package manager
"""

import sys
import os
import argparse
from .config import Config
from .installer import Installer
from .utils import parse_version_spec

def main():
    parser = argparse.ArgumentParser(
        description="Snakeer - A Node.js-style package manager for Python",
        prog="snakeer"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Install command
    install_parser = subparsers.add_parser("install", help="Install all dependencies from project_packages.json")
    install_parser.add_argument("--force", action="store_true", help="Force reinstall all packages")
    
    # Add command
    add_parser = subparsers.add_parser("add", help="Add a new package to dependencies")
    add_parser.add_argument("package", help="Package name with optional version (e.g., coolpkg@1.0.0)")
    
    # Remove command
    remove_parser = subparsers.add_parser("remove", help="Remove a package from dependencies")
    remove_parser.add_argument("package", help="Package name to remove")
    
    # Update command
    update_parser = subparsers.add_parser("update", help="Update packages according to version ranges")
    update_parser.add_argument("package", nargs="?", help="Specific package to update (optional)")
    
    # Publish command
    publish_parser = subparsers.add_parser("publish", help="Publish current package to registry")
    publish_parser.add_argument("--registry", default="https://api.github.com/repos/andy64lol/snakeer_packages_lib",
                               help="Registry URL")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List installed packages")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Initialize config and installer
    config = Config()
    installer = Installer(config)
    
    try:
        if args.command == "install":
            print("📦 Installing dependencies...")
            installer.install_all(force=args.force)
            print("✅ Installation complete!")
            
        elif args.command == "add":
            package_spec = args.package
            if "@" in package_spec:
                name, version = package_spec.rsplit("@", 1)
            else:
                name = package_spec
                version = "latest"
            
            print(f"➕ Adding {name}@{version}...")
            config.add_dependency(name, version)
            installer.install_package(name, version)
            print(f"✅ Added {name}@{version}")
            
        elif args.command == "remove":
            name = args.package
            print(f"➖ Removing {name}...")
            config.remove_dependency(name)
            installer.remove_package(name)
            print(f"✅ Removed {name}")
            
        elif args.command == "update":
            if args.package:
                print(f"🔄 Updating {args.package}...")
                installer.update_package(args.package)
            else:
                print("🔄 Updating all packages...")
                installer.update_all()
            print("✅ Update complete!")
            
        elif args.command == "publish":
            print("📤 Publishing package...")
            installer.publish(args.registry)
            print("✅ Package published!")
            
        elif args.command == "list":
            packages = config.get_installed_packages()
            if packages:
                print("📋 Installed packages:")
                for name, version in packages.items():
                    requested = config.get_requested_version(name)
                    print(f"  • {name}@{version} (requested: {requested})")
            else:
                print("📭 No packages installed")
                
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
