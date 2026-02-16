#!/usr/bin/env python3
"""
Snakeer Package Manager - Entry Point Demo
This demonstrates how to use the Snakeer package manager
"""

import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from snakeer import require, Config, Installer
from snakeer.cli import main as cli_main


def demo_require():
    """Demonstrate the require() function"""
    print("\n" + "="*50)
    print("DEMO: Using require() to load packages")
    print("="*50)
    
    try:
        # Try to load a package (will fail if not installed)
        # coolpkg = require("coolpkg")
        # print(f"Loaded coolpkg: {coolpkg}")
        # result = coolpkg.some_function()
        # print(f"Result: {result}")
        
        print("Note: Install packages first with 'snakeer install'")
        print("Then use: coolpkg = require('coolpkg')")
        
    except ImportError as e:
        print(f"Import error: {e}")


def demo_config():
    """Demonstrate configuration management"""
    print("\n" + "="*50)
    print("DEMO: Configuration Management")
    print("="*50)
    
    config = Config()
    
    print(f"Project name: {config.get_project_name()}")
    print(f"Project version: {config.get_project_version()}")
    print(f"Config path: {config.get_config_path()}")
    
    deps = config.get_dependencies()
    if deps:
        print(f"Dependencies: {deps}")
    else:
        print("No dependencies configured")
        print("Add with: snakeer add <package>@<version>")


def demo_cli():
    """Run the CLI main function"""
    print("\n" + "="*50)
    print("Running Snakeer CLI")
    print("="*50)
    cli_main()


def main():
    """Main entry point"""
    print("🐍 Snakeer Package Manager Demo")
    print("A Node.js-style package manager for Python")
    
    if len(sys.argv) > 1:
        # If arguments provided, run CLI
        demo_cli()
    else:
        # Otherwise run demos
        demo_config()
        demo_require()
        
        print("\n" + "="*50)
        print("USAGE:")
        print("  python main.py <command>  - Run CLI commands")
        print("  snakeer <command>         - Use installed CLI")
        print("="*50)
        print("\nAvailable commands:")
        print("  install          - Install all dependencies")
        print("  add <pkg>@<ver>  - Add a package")
        print("  remove <pkg>     - Remove a package")
        print("  update [pkg]     - Update packages")
        print("  list             - List installed packages")
        print("  publish          - Publish current package")


if __name__ == "__main__":
    main()
