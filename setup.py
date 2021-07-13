#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup
import setuptools  # noqa

__version__ = "1.1.1"
setup(
    name="sim_generator",
    packages=["sim_generator"],
    version=__version__,
    license="MIT",
    description="A little command line utility to generate pattern images for structured illumination microscopy",
    author="Brad Day",
    author_email="bradday4@gmaild.com",
    url="https://github.com/bradday4/SIM_GENERATOR",
    download_url="https://github.com/bradday4/SIM_GENERATOR/releases",
    keywords=[
        "SIM",
        "Structured Illumination Microscopy",
        "Pattern Generation",
    ],  # Keywords that define your package best
    install_requires=["numpy", "scipy", "fire", "pillow"],  # I get to this in a second
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)
