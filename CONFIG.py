# -*- coding: utf-8 -*-
"""
Created on Thu Apr 22 11:34:21 2021

@author: Alex Bell
"""

import pathlib
import sys
from collections import namedtuple

__THIS_DIR__ = pathlib.PurePath(__file__)
DEV_ROOT = __THIS_DIR__.parents[2]
sys.path.append(str(DEV_ROOT))
import packages.rputils as ru

# %% GLOBALS
DEBUG = True

# %% DEPENDENCIES
dependencies = [
    ru.Dependency(name="algi", version="0.0.1", package="packages"),
    ru.Dependency(name="roxy", version="0.0.1", package="packages", alias="rx"),
    ru.Dependency(name="io", version="0312", package="packages"),
    ru.Dependency(name="emma", version="0.1.0", package="packages"),
]

for pkgspecs in dependencies:
    pkgspecs.load(context=sys.modules[__name__], debug=DEBUG)
