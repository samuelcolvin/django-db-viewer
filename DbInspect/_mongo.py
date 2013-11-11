import pymongo, re
from DbInspect._utils import *
from bson.code import Code as BsonCode
import json
import collections
import traceback

class MongoDb(db_comm):
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
    
    def execute(self, code, ex_type = None):
        try:
            self._code_lines = code.split('\n')
            self._get_other_vars()
            if self._source_col is None:
                raise Exception('The souce collection must be defined in the top level of the code'+
                                ' as "source = <collection_name>')
            collection = self._db[self._source_col]
            if ex_type == 'map_reduce':
                if self._dest_col is None:
                    raise Exception('The destination collection must be defined in the top level of the code'+
                                ' as "dest = <collection_name>')
                functions = self._split_functions()
                if 'map' not in functions.keys() or 'reduce' not in functions.keys():
                    raise Exception('Both "map" and "reduce" functions must be defined')
                data = collection.map_reduce(functions['map'], functions['reduce'], self._dest_col)
                data = data.find()
            else:
                json_text = '\n'.join(self._code_lines)
                q_object = self._ordered_json(json_text)
                if ex_type == 'aggregate':
                    data = collection.aggregate(q_object)
                else:
                    data = collection.find(q_object)
            if self._sort:
                sort = self._ordered_json(self._sort)
                data = data.sort(sort.items())
            result, fields = self._process_data(data)
        except Exception, e:
            traceback.print_exc()
            error = 'ERROR %s: %s' % (type(e).__name__, str(e))
            return False, error, None
        else:
            print 'success %d results' % len(result)
            return True, result, fields
    
    def _ordered_json(self, text):
        text = text.strip(' \t')
        print [text]
        if text == '':
            return None
        return json.JSONDecoder(object_pairs_hook=collections.OrderedDict).decode(text)
        
    def close(self):
        pass
        
    def _process_data(self, data):
        data2 = []
        i = 0
        fields = []
        for row in data:
#             print row
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
            label = self._create_label(row[i1], row[i2])
            values = [self._smart_text(v) for v in row.values()]
            data2.append((values, label))
            i += 1
            if i > MAX_ROWS:
                break
        return data2, fields
    
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
        i = 0
        functions = {}
        while True:
            if i >= len(self._code_lines):
                break
            line = self._code_lines[i]
            if 'function' in line:
                endi, name, code = self._process_func(self._code_lines[i:])
                functions[name] = code
                i += endi
            i += 1
        return functions
    
    def _process_func(self, lines):
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




