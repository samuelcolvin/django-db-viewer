import os.path
import platform
from ctypes import *
from collections import OrderedDict

import bson

import cmongo

print 'markets.markets_value all:'
all_values = cmongo.all_query('127.0.0.1', 27017, 'markets.markets_value')
print len(all_values.split('\n'))
print 'markets.markets_trace filtered on "{"exchange_id": 1}":'
print cmongo.filter_query('127.0.0.1', 27017, 'markets.markets_trace', '{"exchange_id": 1}')
