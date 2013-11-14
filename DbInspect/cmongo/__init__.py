import os.path
import platform
from ctypes import *
from collections import OrderedDict

import bson

cmongo = None

def _load_cmongo_lib():
    """Loads the cmonary CDLL library (from the directory containing this module)."""
    global cmongo
    thismodule = __file__
    abspath = os.path.abspath(thismodule)
    moduledir = list(os.path.split(abspath))[:-1]
    cmonary_fname = "cmongo.so"
    cmonaryfile = os.path.join(*(moduledir + [cmonary_fname]))
    cmongo = CDLL(cmonaryfile)

_load_cmongo_lib()