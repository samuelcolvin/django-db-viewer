import MySQLdb as mdb
from django.utils.encoding import smart_text

MAX_ROWS = 1000

class SqlBase(object):
    _tables = None
    _field_names = None
    
    def get_tables(self):
        if self._tables is None:
            self._tables, self._field_names = self._get_tables()
        return self._tables, self._field_names
        
    def get_fields(self, t_name):
        return self._execute_get_descrition('SELECT * FROM %s LIMIT 1' % t_name)
    
    def get_values(self, t_name, limit = 20):
        self._execute('SELECT * FROM %s LIMIT %d' % (t_name, limit))
        return self._process_data(self.cur.fetchall())[0]
    
    def execute(self, sql):
        try:
            self._execute(sql, close_on_error = False)
            data = self.cur.fetchall()
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
        
    def _process_data(self, data):
        fields = [col[0] for col in self.cur.description]
        name_fields = [i for i, f in enumerate(fields) if 'name' in f]
        i2 = 1
        if len(name_fields) > 0:
            i2 = name_fields[0]
        data2 = []
        i = 0
        for row in data:
            values = [self._smart_text(d) for d in row]
            label = '%s: %s' % (values[0][:10], values[i2][:20])
            data2.append((values, label))
            i += 1
            if i > MAX_ROWS:
                break
        return data2, fields
    
    def _smart_text(self, value):
        try:
            return smart_text(value)
        except:
            return 'unknown character'
    
    def _execute_get_descrition(self, sql):
        self._execute(sql)
        fields = []
        for col in self.cur.description:
            self._process_column(col, fields)
        return fields
                
    def _execute(self, command, close_on_error = True):
        try:
            self.cur.execute(command)
        except Exception, e:
            print "Error: %s" % str(e)
            print 'SQL: %s' % command
            if close_on_error:
                self._close()
            raise(e)
    
    def _close(self):
        try:
            self.con.close()
        except:
            pass
    
    def _setup_types(self):
        self._types = {}
        for t in dir(mdb.constants.FIELD_TYPE):
            if not t.startswith('_'):
                v = getattr(mdb.constants.FIELD_TYPE, t)
                self._types[v] = t