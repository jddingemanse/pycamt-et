# -*- coding: utf-8 -*-
"""
Created on Tue Jun 14 10:08:31 2022

@author: jandirk
"""

from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="pycamtET",  # Required
    version="0.0.3",  # Required
    description="Meteorogly analysis for Ethiopia",  # Optional
    long_description=long_description,  # Optional
    long_description_content_type="text/markdown",  # Optional (see note above)
    url="https://github.com/pypa/sampleproject",  # Optional
    author="Jan Dirk Dingemanse",  # Optional
    author_email="johannesdirk.dingemanse@amu.edu.et",  # Optional
    classifiers=[  # Optional
        "Development Status :: 3 - Alpha",
        # Pick your license as you wish
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
    keywords="meteorology, climate",  # Optional
    package_dir={"": "src"},  # Optional
    packages=find_packages(where="src"),  # Required
    python_requires=">=3.6",
    install_requires=["pandas","matplotlib"],  # Optional
)
