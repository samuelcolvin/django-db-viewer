import os, sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
import DbInspect
import DbInspect.pipe as db_pipe
import DbViewer.models as m
from time import time

class Funcs(object):
    
    @staticmethod
    def mysql_to_mongo(interactive):
        done_tables = ['markets_article', 'markets_sourceupdate', 'markets_updateattempt']
        source_db = m.Database.objects.get(name='markets')
        dest_db = m.Database.objects.get(name='markets_mongo')
        source_comms = source_db.get_comms()
        dest_comms = dest_db.get_comms()
        tables = []
        for table, _ in source_comms.get_tables()[0]:
            if table.startswith('markets_') and table not in done_tables:
                tables.append(table)
        print tables
        start = time()
        db_pipe.SQL_to_MongoDB_multiple_complete(source_comms, dest_comms, tables)
        diff = time() - start
        print 'Time taken: %0.3fs' % diff

    @staticmethod
    def x_exit_without_doing_anything(interactive):
        if interactive:
            raw_input('About to exit, press enter to continue: ')
        print 'exitting'
        pass
        
useage = 'useage: python setup.py [function_name], where function_name can be found by running without an argument'
if len(sys.argv) == 1:
    print 'Choices:'
    options = [func for func in dir(Funcs) if not func.startswith('_')]
    options = dict(zip(range(1, 1+len(options)), options))
    for (i, func) in options.items():
        print '%d >> %s' % (i, func)
    choice = input('\nEnter your choice of function to call by number: ')
    function_name = options[choice]
    interactive = True
elif len(sys.argv) == 2:
    function_name = sys.argv[1]
    interactive = False
else:
    print 'ERROR: arguments are wrong, system arguments: %s' % str(sys.argv)
    print useage
    sys.exit(2)
if not hasattr(Funcs, function_name):
    print 'ERROR: "%s" is not the name of an available function, call with no arguments to list available functions.' % function_name
    print useage
else:
    print '\n   ***calling %s, Interactive %r***\n' % (function_name, interactive)
    getattr(Funcs, function_name)(interactive)