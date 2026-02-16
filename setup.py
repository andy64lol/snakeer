#!/usr/bin/env python3
"""
Setup script for Snakeer package manager
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="snakeer",
    version="1.0.0",
    author="andy64lol",
    author_email="andy64lol@example.com",
    description="A Node.js-style package manager for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/andy64lol/snakeer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
    ],
    entry_points={
        "console_scripts": [
            "snakeer=snakeer.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
