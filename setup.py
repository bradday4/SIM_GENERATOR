#!/usr/bin/env python
# -*- coding: utf-8 -*-
from distutils.core import setup

import setuptools  # noqa

BASEPKG = ["numpy", "scipy", "pillow", "pyfiglet"]

TESTPKG = ["flake8", "pytest", "black"] + BASEPKG
DEVPKG = ["pre-commit"] + TESTPKG

__version__ = "1.3.8"
setup(
    name="sim_generator",
    packages=["sim_generator"],
    version=__version__,
    license="MIT",
    description="A little command line utility to generate pattern images for structured illumination microscopy",
    author="Brad Day",
    author_email="bradday4@gmail.com",
    url="https://github.com/bradday4/SIM_GENERATOR",
    download_url="https://github.com/bradday4/SIM_GENERATOR/releases",
    keywords=[
        "SIM",
        "Structured Illumination Microscopy",
        "Pattern Generation",
    ],  # Keywords that define your package best
    install_requires=BASEPKG,
    extras_require={"test": TESTPKG, "dev": DEVPKG},
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)
