import MySQLdb as mdb
from django.utils.encoding import smart_text
from DbInspect._settings import *

class db_comm(object):
    def _smart_text(self, value):
        try:
            return smart_text(value)
        except:
            return 'unknown character'
        
    def _create_label(self, v1, v2):
        v2 =  self._smart_text(v2)
        label = '%s: %s' % (self._smart_text(v1)[:10], v2[:20])
        if len(v2) > 20:
            label = label[:-3] + '...'
        return label

class SqlBase(db_comm):
    _tables = None
    _field_names = None
    
    def get_tables(self):
        if self._tables is None:
            self._tables, self._field_names = self._get_tables()
        return self._tables, self._field_names
        
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
    
    def execute(self, sql):
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
            except:
                pass