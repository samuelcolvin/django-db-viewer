import os.path
import platform
from ctypes import *
from collections import OrderedDict

import bson

import cmongo

print cmongo.all_query('127.0.0.1', 27017, 'markets.markets_trace')
