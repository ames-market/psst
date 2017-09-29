# -*- coding: utf-8 -*-

"""
psst

A free & open-source Power System Simulation Toolbox written entirely in Python.
"""

from .__version__ import __title__, __description__, __url__, __version__
from .__version__ import __author__, __author_email__, __license__, __copyright__


# Let users know if they're missing hard dependencies
hard_dependencies = ('pyomo', 'pandas',)
missing_dependencies = []

for dependency in hard_dependencies:
    try:
        __import__(dependency)
    except ImportError as e:
        missing_dependencies.append(dependency)

if missing_dependencies:
    raise ImportError(
        "Missing required dependencies {0}".format(missing_dependencies))
del hard_dependencies, missing_dependencies

# Todo: Should this import key classes and modules?
