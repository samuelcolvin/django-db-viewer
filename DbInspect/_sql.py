import MySQLdb as mdb
import sqlite3
from DbInspect._utils import *
import pandas.io.sql as psql
import StringIO

class _SqlBase(db_comm):
    _con=None
    
    def __init__(self, dbsets):
        self._dbsets = dbsets
        self._setup_types()
        self._con_cur()
        self.db_name = dbsets['db_name']
    
    def _con_cur(self):
        if not self._con:
            self._con = self._get_con()
            self._cur = self._con.cursor()
    
    def get_tables(self):
        tables, field_names = self._get_tables()
        return tables, field_names
        
    def get_fields(self, t_name):
        cur, fields = self._execute_get_descrition('SELECT * FROM %s LIMIT 1' % t_name)
        values = cur.fetchone()
        if values:
            for field, v in zip(fields, values):
                if field[1] is None:
                    field[1] = type(v).__name__
        self._close()
        return fields
    
    def get_values(self, t_name, limit = 20):
        cur = self._execute('SELECT * FROM %s LIMIT %d' % (t_name, limit))
        return self._process_data(cur.fetchall())[0]
    
    def execute(self, sql, ex_type = None):
        try:
            cur = self._execute(sql)
            data = cur.fetchall()
        except mdb.Error, e:
            error = 'ERROR %s: %s' % (type(e).__name__, e.args[1])
            return False, error, None
        except Exception, e:
            error = 'ERROR %s: %s' % (type(e).__name__, str(e))
            return False, error, None
        else:
            result, fields = self._process_data(data)
            print 'success %d results' % len(result)
            return True, result, fields
        finally:
            self._close()
            
    def generate_csv(self, sql):
        try:
            self._con_cur()
            dbase = psql.frame_query(sql, con=self._con)
            file_stream = StringIO.StringIO()
            dbase.to_csv(file_stream)
            file_stream.seek(0)
            return file_stream
        except Exception, e:
            print "Error: %s" % str(e)
            self._close()
            raise(e)
                
    def _execute(self, command):
        try:
            self._con_cur()
            self._cur.execute(command)
            return self._cur
        except Exception, e:
            print "Error: %s" % str(e)
            print 'SQL: %s' % command
            self._close()
            raise(e)
        
    def _process_data(self, data):
        fields = [col[0] for col in self._cur.description]
        name_fields = [i for i, f in enumerate(fields) if 'name' in f]
        i2 = 1
        if len(name_fields) > 0:
            i2 = name_fields[0]
        data2 = []
        i = 0
        for row in data:
            label = self._create_label(row[0], row[i2])
            values = [self._smart_text(d) for d in row]
            data2.append((values, label))
            i += 1
            if i > MAX_ROWS:
                break
        self._close()
        return data2, fields
    
    def _execute_get_descrition(self, sql):
        cur = self._execute(sql)
        fields = []
        for col in cur.description:
            self._process_column(col, fields)
        return cur, fields
    
    def _setup_types(self):
        self._types = {}
        for t in dir(mdb.constants.FIELD_TYPE):
            if not t.startswith('_'):
                v = getattr(mdb.constants.FIELD_TYPE, t)
                self._types[v] = t
        
    def _close(self):
            try:
                self._con.close()
                self._con = None
            except:
                pass

class MySql(_SqlBase):
            
    def _get_con(self):
        return mdb.connect(self._dbsets['host'], self._dbsets['username'], 
                               self._dbsets['password'], self._dbsets['db_name'], port=self._dbsets['port'])
            
        
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
        tables = []
        cur, fields = self._execute_get_descrition('SHOW TABLE STATUS')
        field_names = [i[0] for i in fields]
        for t_info in cur.fetchall():
            tables.append((t_info[0], t_info))
        self._close()
        return tables, field_names
    
    def _process_column(self, col, fields):
        fields.append([col[0], self._types[col[1]]])

class SqlLite(_SqlBase):
        
    def _get_con(self):
        return sqlite3.connect(self._dbsets['path'])

    def get_version(self):
        return sqlite3.sqlite_version
    
    def get_databases(self):
        return []
    
    def _get_tables(self):
        tables = []
        cur, fields = self._execute_get_descrition("SELECT * FROM sqlite_master WHERE type='table';")
        field_names = [i[0] for i in fields]
        for t_info in cur.fetchall():
            tables.append((t_info[1], t_info))
        self._close()
        return tables, field_names
    
    def _process_column(self, col, fields):
        fields.append([col[0], None])

