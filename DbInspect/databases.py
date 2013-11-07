import MySQLdb as mdb
from DbInspect import _sql
import sqlite3

class MySql(_sql.SqlBase):
    _tables = None
    
    def __init__(self, dbsets):
        self.con=None
        self._setup_types()
        try:
            self.con = mdb.connect(dbsets['host'], dbsets['username'], 
                                   dbsets['password'], dbsets['db_name'], port=dbsets['port'])
            self.cur = self.con.cursor()
        except mdb.Error, e:
            print "Error %d: %s" % (e.args[0],e.args[1])
            self._close()
        
    def get_version(self):
        self._execute('SELECT VERSION()')
        return self.cur.fetchone()
    
    def _get_tables(self):
        self._tables = []
        fields = self._execute_get_descrition('SHOW TABLE STATUS')
        field_names = [i[0] for i in fields]
        for t_info in self.cur.fetchall():
            self._tables.append((t_info[0], t_info))
        return self._tables, field_names
    
    def _process_column(self, col, fields):
        fields.append((col[0], self._types[col[1]]))

class SqlLite(_sql.SqlBase):
    _tables = None
    
    def __init__(self, dbsets):
        self.con=None
        self._setup_types()
        try:
            self.con = sqlite3.connect(dbsets['path'])
            self.cur = self.con.cursor()
        except Exception, e:
            print 'ERROR %s: %s' % (type(e).__name__, str(e))
            self._close()
    
    def get_version(self):
        return 'unknown'
    
    def _get_tables(self):
        self._tables = []
        fields = self._execute_get_descrition("SELECT * FROM sqlite_master WHERE type='table';")
        field_names = [i[0] for i in fields]
        for t_info in self.cur.fetchall():
            self._tables.append((t_info[1], t_info))
        return self._tables, field_names
    
    def _process_column(self, col, fields):
        fields.append((col[0], None))





