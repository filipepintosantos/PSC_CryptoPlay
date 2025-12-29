"""Setup configuration for PSC CryptoPlay."""
from setuptools import setup, find_packages
import os
import re

# Read version from src/__init__.py
def get_version():
    init_path = os.path.join(os.path.dirname(__file__), 'src', '__init__.py')
    with open(init_path, 'r', encoding='utf-8') as f:
        content = f.read()
        match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
        if match:
            return match.group(1)
    raise RuntimeError('Unable to find version string')

setup(
    name="psc-cryptoplay",
    version="4.3.7",
    packages=find_packages(exclude=["tests*"]),
    python_requires=">=3.8",
    install_requires=[
        "yfinance",
        "openpyxl",
        "pandas",
        "requests",
    ],
)
