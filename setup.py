#!/usr/bin/env python

import os
import setuptools

install_requires = [
    line.rstrip() for line in open(os.path.join(os.path.dirname(__file__), "REQUIREMENTS.txt"))
]

setuptools.setup(
    name="starspace",
    packages=setuptools.find_packages(),
    install_requires=install_requires,
    include_package_data=True,
    version="0.0.1",
)