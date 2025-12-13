"""Setup configuration for PSC CryptoPlay."""
from setuptools import setup, find_packages

setup(
    name="psc-cryptoplay",
    version="3.2.0",
    packages=find_packages(exclude=["tests*"]),
    python_requires=">=3.8",
    install_requires=[
        "yfinance",
        "openpyxl",
        "pandas",
        "requests",
    ],
)
