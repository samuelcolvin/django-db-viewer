import DbInspect
import subprocess
import DbInspect._utils as utils

def SQL_to_MongoDB_multiple_complete(source_comms, dest_comms, tables):
    sql2mongo = SQL_to_MongoDB(source_comms, dest_comms)
    msgs = []
    for table in tables:
        query = 'SELECT * FROM %s' % table # LIMIT 100
        msg = sql2mongo.run_query(query, table)
        msgs.extend(msg)
    return msgs
    

class SQL_to_MongoDB(object):
    verbose_name = 'SQL to MongoDb'
    source_type = (DbInspect.SqlLite, DbInspect.MySql)
    dest_type = (DbInspect.MongoDb)
    cancel_if_table_exists = False
    delete_existing_tables = True
    
    def __init__(self, source, dest):
        self._source = source
        self._dest = dest
        colls = dest.get_tables()[0]
        self._collections = [name for name, _ in colls]
        
    def run_query(self, query, coll_name):
        msgs = ['Collection: %s' % coll_name]
        if coll_name in self._collections:
            if self.cancel_if_table_exists:
                msgs.append('Table exists and cancel_if_table_exists is True, not adding')
                return msgs
            if self.delete_existing_tables:
                msgs.append('Deleting existing collection')
                self._dest.db[coll_name].drop()
        command = self._get_command(self._dest.dbsets, coll_name)
        msgs.append('Import Call: ' + ' '.join(command))
        file_stream = self._source.generate_csv(query)
        p = subprocess.Popen(command, stdin=subprocess.PIPE, 
                                      stdout = subprocess.PIPE, 
                                      stderr = subprocess.PIPE)
        text = utils.super_smart_text(file_stream.getvalue())
        if text.startswith(',id'):
            text = text.replace(',id', ',_id', 1)
        stdout, stderr = p.communicate(input = text)
        msgs.append('SDTERR: %s' % stderr)
        msgs.append('STDOUT:')
        msgs.extend(stdout.split('\n'))
        return msgs
        
    def _get_command(self, dbsets, coll):
        args = dbsets.copy()
        args['coll'] = coll
        c = 'mongoimport -h %(host)s -p %(port)s -d %(db_name)s -c %(coll)s --type csv --headerline ' % args
        return c.split(' ')





