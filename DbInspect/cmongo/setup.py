from distutils.core import setup, Extension
VERSION = '0.1'

cmongo = Extension('cmongo', 
                    define_macros = [('MAJOR_VERSION', '0'),
                                     ('MINOR_VERSION', '1')],
                    include_dirs = ['/usr/local/include'],
                    libraries = ['mongoc'],
                    library_dirs = ['/usr/local/lib'],
                    sources = ['cmongo.c'],
                    extra_compile_args=['--std=c99'])

setup (name = 'MongoC',
       version = VERSION,
       description = 'performs mongodb queries in c and returns csv results',
       author = 'Samuel Colvin',
       author_email = 'S@muelColvin.com',
       long_description = '''
Package inspired by monary but complete rewritten.
''',
       ext_modules = [cmongo])