import pymongo, re
from DbInspect._utils import *
from bson.code import Code as BsonCode
import json
import collections
import traceback
import StringIO
import pandas as pd
import numpy

class MongoDb(db_comm):
    
    def __init__(self, dbsets):
        try:
            self._client = pymongo.MongoClient(dbsets['host'], dbsets['port'])
            self.db = self._client[dbsets['db_name']]
            self.dbsets = dbsets
        except Exception, e:
            msg = 'CONNECTION ERROR %s: %s' % (type(e).__name__, str(e))
            print msg
            raise Exception(msg)
            
    def get_version(self):
        return pymongo.version
    
    def get_databases(self):
        return self._client.database_names()
    
    def get_tables(self):
        tables = []
        for name in self.db.collection_names():
            tables.append((name, (name, self.db[name].count())))
        field_names = ('name', 'count')
        return tables, field_names
        
    def get_table_fields(self, t_name):
        f = self.db[t_name].find_one()
        if f:
            return [(k, type(v).__name__) for k, v in f.items()]
        return []
    
    def get_query_fields(self, code, ex_type = None):
        cursor = self._execute(code, ex_type)
        for row in cursor:
            return [(k, type(v).__name__) for k, v in row.items()]
        return []
    
    def get_values(self, t_name, limit = SIMPLE_LIMIT):
        c = self.db[t_name].find(limit=limit)
        return self._process_data(c)[0]
    
    def execute(self, code, ex_type = None):
        try:
            cursor = self._execute(code, ex_type)
            result, fields = self._process_data(cursor)
        except Exception, e:
            traceback.print_exc()
            error = 'ERROR %s: %s' % (type(e).__name__, str(e))
            return False, error, None
        else:
            return True, result, fields
        
    def get_pandas(self, code, ex_type = None):
        try:
            cursor = self._execute(code, ex_type)
            return pd.DataFrame(list(cursor))
        except Exception, e:
            print "Error: %s" % str(e)
            self._close()
            raise(e)
            
    def generate_string(self, code, string_format = 'csv', ex_type = None):
        df = self.get_pandas(code, ex_type)
        return self._to_csv(df, code, string_format)
    
    def insert_pandas(self, t_name, df):
        collection = self.db[t_name]
        columns = list(df.columns)
        if 'id' in columns:
            columns[columns.index('id')] = '_id'
        i = -1
        int64_col = False
        for c in df.columns:
            if df[c].dtype == numpy.int64:
                int64_col = True
                break
        for i, row in enumerate(df.values):
            row_dict = dict(zip(columns, row))
            # TODO: surely there should be something better than this
            if int64_col:
                for k, v in row_dict.items():
                    if isinstance(v, numpy.int64):
                        row_dict[k] = int(v)
            if i == 0:
                print '    %r' % row_dict
                for k, v in row_dict.items():
                    print '    %s: %s (%s)' % (k, v, type(v))
            return 0
            collection.insert(row_dict)
        return i + 1
    
    def _execute(self, code, ex_type = None):
        self._code_lines = code.split('\n')
        self._get_other_vars()
        if self._source_col is None:
            raise Exception('The souce collection must be defined in the top level of the code'+
                            ' as "source = <collection_name>')
        collection = self.db[self._source_col]
        if ex_type == 'map_reduce':
            if self._dest_col is None:
                raise Exception('The destination collection must be defined in the top level of the code'+
                            ' as "dest = <collection_name>')
            functions = self._split_functions()
            if 'map' not in functions.keys() or 'reduce' not in functions.keys():
                raise Exception('Both "map" and "reduce" functions must be defined')
            cursor = collection.map_reduce(functions['map'], functions['reduce'], self._dest_col)
            cursor = cursor.find()
        else:
            json_text = '\n'.join(self._code_lines)
            q_object = self._ordered_json(json_text)
            if ex_type == 'aggregate':
                cursor = collection.aggregate(q_object)
            else:
                cursor = collection.find(q_object)
        if self._sort:
            sort = self._ordered_json(self._sort)
            cursor = cursor.sort(sort.items())
        return cursor
    
    def _ordered_json(self, text):
        text = text.strip(' \t')
        if text == '':
            return None
        return json.JSONDecoder(object_pairs_hook=collections.OrderedDict).decode(text)
        
    def close(self):
        pass
        
    def _process_data(self, cursor):
        data = []
        i = 0
        fields = []
        for row in cursor:
            if i == 0:
                fields = row.keys()
                i1 = fields[0]
                if '_id' in fields: i1 = '_id'
                i2 = fields[1]
                if i1 == i2:
                    i2 = fields[0]
                for k in fields:
                    if 'name' in k:
                        i2 = k
                        break
            try:
                label = self._create_label(row[i1], row[i2])
            except KeyError:
                l1 = '*'
                l2 = '*'
                try: l1 = row[i1]
                except: pass
                try: l2 = row[i2]
                except: pass
                label = self._create_label(l1, l2)
            values = [self._smart_text(v) for v in row.values()]
            data.append((values, label))
            i += 1
            if i > MAX_ROWS:
                break
        return data, fields
    
    def _get_other_vars(self):
        to_find = {'source': None, 'dest': None, 'sort': None}
        lines = self._code_lines[:]
        for line in lines:
            for k, v in to_find.items():
                if re.search(k + ' *=', line)  and not v and not 'function' in line:
                    if k == 'sort':
                        to_find[k] = line[line.index('=') + 1:].replace(';', '')
                        self._code_lines.remove(line)
                    else:
                        to_find[k] = self._get_value_remove(line)
                    break
            if None not in to_find.values():
                break
        self._source_col = to_find['source']
        self._dest_col = to_find['dest']
        self._sort = to_find['sort']
    
    def _get_value_remove(self, line): 
        v = re.findall('\w+', line[line.index('='):])[0]
        self._code_lines.remove(line)
        return v
    
    def _split_functions(self):
        def process_func(lines):
            name = re.findall('\w+', lines[0].replace('function', ''))[0]
            brackets = 0
            started = False
            for ii, line in enumerate(lines):
                for c in line:
                    if c == '{':
                        brackets +=1
                        started = True
                    if c == '}':
                        brackets -=1
                if brackets == 0 and started:
                    code = '\n'.join(lines[:ii + 1])
                    return ii, name, code
        i = 0
        functions = {}
        while True:
            if i >= len(self._code_lines):
                break
            line = self._code_lines[i]
            if 'function' in line:
                endi, name, code = process_func(self._code_lines[i:])
                functions[name] = code
                i += endi
            i += 1
        return functions




