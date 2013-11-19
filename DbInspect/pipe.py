import DbInspect
import subprocess
import DbInspect._utils as utils

def simple_printer(line):
    print line

def SQL_to_MongoDB_all_complete(source_comms, dest_comms, printer = simple_printer):        
        tables = []
        for table, _ in source_comms.get_tables()[0]:
            tables.append(table)
        SQL_to_MongoDB_multiple_complete(source_comms, dest_comms, tables, printer)

def SQL_to_MongoDB_multiple_complete(source_comms, dest_comms, tables, printer = simple_printer):
    sql2mongo = SQL_to_MongoDB(source_comms, dest_comms, printer)
    for table in tables:
        query = 'SELECT * FROM %s' % table # LIMIT 100
        sql2mongo.run_query(query, table)
    

class SQL_to_MongoDB(object):
    verbose_name = 'SQL to MongoDb'
    source_type = (DbInspect.SqlLite, DbInspect.MySql)
    dest_type = (DbInspect.MongoDb)
    cancel_if_table_exists = False
    delete_existing_tables = True
    
    def __init__(self, source, dest, printer = simple_printer):
        self._source = source
        self._dest = dest
        self._printer = printer
        colls = dest.get_tables()[0]
        self._collections = [name for name, _ in colls]
        
    def run_query(self, query, coll_name):
        self._printer('Collection: %s' % coll_name)
        if coll_name in self._collections:
            if self.cancel_if_table_exists:
                self._printer('Table exists and cancel_if_table_exists is True, not adding')
            if self.delete_existing_tables:
                self._printer('Deleting existing collection')
                self._dest.db[coll_name].drop()
        
        df = self._source.get_pandas(query)
        items = self._dest.insert_pandas(coll_name, df)
        self._printer('Added %d items' % items)

    def run_query_external(self, query, coll_name):
        self._printer('Collection: %s' % coll_name)
        if coll_name in self._collections:
            if self.cancel_if_table_exists:
                self._printer('Table exists and cancel_if_table_exists is True, not adding')
            if self.delete_existing_tables:
                self._printer('Deleting existing collection')
                self._dest.db[coll_name].drop()
        command = self._get_command(self._dest.dbsets, coll_name)
        self._printer('Import Call: ' + ' '.join(command))
         
        text = self._source.generate_string(query, 'json')
        text = utils.super_smart_text(text)
        print text[:1000]
        p = subprocess.Popen(command, stdin = subprocess.PIPE, 
                                      stdout = subprocess.PIPE, 
                                      stderr = subprocess.PIPE)
        if text.startswith(',id'):
            text = text.replace(',id', ',_id', 1)
        stdout, stderr = p.communicate(input = text)
        self._printer('SDTERR: %s' % stderr)
        self._printer('STDOUT:')
        self._printer(stdout.split('\n'))
        
    def _get_command(self, dbsets, coll):
        args = dbsets.copy()
        args['coll'] = coll
        c = 'mongoimport -h %(host)s -p %(port)s -d %(db_name)s -c %(coll)s --type json' % args # --headerline 
        return c.split(' ')





