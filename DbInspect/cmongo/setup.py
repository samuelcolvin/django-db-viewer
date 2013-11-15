"""
to compile with gcc: gcc --std=c99 json2bson.c -I /usr/include/json  cmongo.c -lmongoc -ljson-c -o mong_test

build, mv: rm -rf build cmongo.so; python setup.py build; cp build/lib.linux-x86_64-2.7/cmongo.so .; rm -rf build
"""
from distutils.core import setup, Extension
VERSION = '0.1'

cmongo = Extension('cmongo', 
                    define_macros = [('PYTHON', '1')],
                    include_dirs = ['/usr/local/include'],
                    libraries = ['json-c', 'mongoc'],
                    library_dirs = ['/usr/local/lib'],
                    sources = ['json2bson.c', 'cmongo.c'],
                    extra_compile_args=['--std=c99'])

setup (name = 'cmongo',
       version = VERSION,
       description = 'performs mongodb queries in c and returns csv results',
       author = 'Samuel Colvin',
       author_email = 'S@muelColvin.com',
       long_description = '''
Package inspired by monary but completely rewritten.
''',
       ext_modules = [cmongo])