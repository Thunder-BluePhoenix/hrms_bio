#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open("requirements.txt", "r") as f:
    install_requires = [line.strip() for line in f.read().splitlines() 
                       if line.strip() and not line.startswith("#")]

# Read version from __init__.py
exec(open("hrms_biometric/__init__.py").read())

setup(
    name="hrms_biometric",
    version=__version__,
    description="Biometric face recognition attendance system for Frappe/ERPNext",
    author="BluePhoenix",
    author_email="bluephoenix00995@gmail.com",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires,
    python_requires=">=3.10",
)