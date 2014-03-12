#!/usr/bin/env/python

from distutils.core import setup

setup(
    name='RPiLiquidCrystal',
    version='0.1.0',
    author='Fernando Chorney',
    author_email='python@djsbx.com',
    packages=['RPiLiquidCrystal'],
    url='http://pypi.python.org/pypi/RPiLiquidCrystal/',
    license='LICENSE.txt',
    description='Python port of the Arduino LiquidCrystal library for use with the Raspberry Pi',
    long_description=open('README.txt').read(),
)
