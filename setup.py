# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name="financialdataimporter",
    version="0.1.1",
    author="Nils Döring",
    author_email="ndoering@students.uni-mainz.de",
    description="A simple importer for financial market data from Yahoo Finance with caching function.",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/OriginalNils/FinancialDataImporter", # Optional: Link zum GitHub-Repo
    
    install_requires=[
        "pandas>=1.0.0",  # Wir geben an, dass wir mindestens Version 1.0.0 von pandas benötigen
        "yfinance>=0.1.63"
    ],
    
    packages=find_packages(),
    
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Office/Business :: Financial :: Investment",
    ],
    python_requires='>=3.6',
)
