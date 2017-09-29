#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from codecs import open
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))

# TODO: Testing stuff goes here?

packages = ['psst']

requirements = [
    'click',
    'sphinx',
    'ghp-import',
    'sphinxcontrib-fulltoc',
    'sphinxcontrib-jsdemo',
    'nbsphinx',
    'pandas',
    'future',
    'networkx',
    'matplotlib',
    'pyomo',
    'pypower',
    'ipywidgets',
    'bqplot',
    'traittypes',
]

# TODO: put package test requirements here
test_requirements = []

about = {}
with open(os.path.join(here, 'psst', '__version__.py'), 'r', encoding='utf-8') as f:
    exec(f.read(), about)

with open('README.md', 'r', encoding='utf-8') as f:
    readme = f.read()
with open('HISTORY.rst', 'r', encoding='utf-8') as f:
    history = f.read()

setup(
    name=about['__title__'],
    version=about['__version__'],
    description=about['__description__'],
    long_description=readme + '\n\n' + history,
    author=about['__author__'],
    author_email=about['__author_email__'],
    url=about['__url__'],
    packages=packages,
    package_dir={'psst': 'psst'},
    entry_points={'console_scripts': ['psst=psst.cli:cli']},
    include_package_data=True,
    install_requires=requirements,
    license=about['__license__'],
    zip_safe=False,
    keywords='psst',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Scientific/Engineering'
    ],
    test_suite='tests',
    tests_require=test_requirements
)
