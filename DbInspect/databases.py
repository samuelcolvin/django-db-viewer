import MySQLdb as mdb
from DbInspect import _sql
import sqlite3
import pymongo
from bson.code import Code
from DbInspect._settings import *

class MySql(_sql.SqlBase):
    _tables = None
    
    def __init__(self, dbsets):
        self.con=None
        self._setup_types()
        try:
            self.con = mdb.connect(dbsets['host'], dbsets['username'], 
                                   dbsets['password'], dbsets['db_name'], port=dbsets['port'])
            self._cur = self.con.cursor()
        except mdb.Error, e:
            print "Error %d: %s" % (e.args[0],e.args[1])
            self._close()
        
    def get_version(self):
        cur = self._execute('SELECT VERSION()')
        return cur.fetchone()
    
    def get_databases(self):
        cur = self._execute('SHOW DATABASES')
        dbs = []
        for d_info in cur.fetchall():
            dbs.append(d_info[0])
        self._close()
        return dbs
    
    def _get_tables(self):
        self._tables = []
        cur, fields = self._execute_get_descrition('SHOW TABLE STATUS')
        field_names = [i[0] for i in fields]
        for t_info in cur.fetchall():
            self._tables.append((t_info[0], t_info))
        self._close()
        return self._tables, field_names
    
    def _process_column(self, col, fields):
        fields.append([col[0], self._types[col[1]]])
                
    def _execute(self, command):
        try:
            self._cur.execute(command)
            return self._cur
        except Exception, e:
            print "Error: %s" % str(e)
            print 'SQL: %s' % command
#             self.close()
            raise(e)

class SqlLite(_sql.SqlBase):
    _tables = None
    
    def __init__(self, dbsets):
        self._setup_types()
        self._dbsets = dbsets
    
    def get_version(self):
        return sqlite3.sqlite_version
    
    def get_databases(self):
        return []
    
    def _get_tables(self):
        self._tables = []
        cur, fields = self._execute_get_descrition("SELECT * FROM sqlite_master WHERE type='table';")
        field_names = [i[0] for i in fields]
        for t_info in cur.fetchall():
            self._tables.append((t_info[1], t_info))
        self._close()
        return self._tables, field_names
    
    def _process_column(self, col, fields):
        fields.append([col[0], None])
                
    def _execute(self, command):
        try:
            self._con = sqlite3.connect(self._dbsets['path'])
            self._cur = self._con.cursor()
            self._cur.execute(command)
            return self._cur
        except Exception, e:
            print "Error: %s" % str(e)
            print 'SQL: %s' % command
            self._close()
            raise(e)

class MongoDb(_sql.db_comm):
    _tables = None
    
    def __init__(self, dbsets):
        try:
            self._client = pymongo.MongoClient(dbsets['host'], dbsets['port'])
            self._db = self._client[dbsets['db_name']]
        except Exception, e:
            msg = 'CONNECTION ERROR %s: %s' % (type(e).__name__, str(e))
            print msg
            raise Exception(msg)
            
    def get_version(self):
        return pymongo.version
    
    def get_databases(self):
        return self._client.database_names()
    
    def get_tables(self):
        if self._tables is None:
            self._tables = []
            for name in self._db.collection_names():
                self._tables.append((name, (name, self._db[name].count())))
            self._field_names = ('name', 'count')
        return self._tables, self._field_names
        
    def get_fields(self, t_name):
        f = self._db[t_name].find_one()
        if f:
            return [(k, type(v).__name__) for k, v in f.items()]
        return []
    
    def get_values(self, t_name, limit = SIMPLE_LIMIT):
        c = self._db[t_name].find(limit=limit)
        return self._process_data(c)[0]
    
    def execute(self, sql):
        try:
            raise Exception('not implemented')
            data = None
        except Exception, e:
            error = 'ERROR %s: %s' % (type(e).__name__, str(e))
            return False, error, None
        else:
            result, fields = self._process_data(data)
            print 'success %d results' % len(result)
            return True, result, fields
        
    def close(self):
        pass
        
    def _process_data(self, data):
        data2 = []
        i = 0
        fields = []
        for row in data:
            print row
            if i == 0:
                fields = row.keys()
                i1 = fields[0]
                if '_id' in fields: i1 = '_id'
                i2 = fields[1]
                for k in fields:
                    if 'name' in k:
                        i2 = k
                        break
            label = self._create_label(row[i1], row[i2])
            values = [self._smart_text(v) for v in row.values()]
            data2.append((values, label))
            i += 1
            if i > MAX_ROWS:
                break
        return data2, fields



