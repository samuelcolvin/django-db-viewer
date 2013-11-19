import re
import chardet
import StringIO

MAX_ROWS = 1000
SIMPLE_LIMIT = 50

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

    def _to_csv(self, dataframe, code):
        fields = self.get_query_fields(code)
        field_names = [f[0] for f in fields]
        name_convert = {}
        for c in dataframe.columns:
            if dataframe[c].dtype == '<M8[ns]':
                dataframe[c] = dataframe[c].apply(lambda x: x.strftime('%s'))
            if c == '':
                dataframe.drop('', 1)
            elif c in field_names:
                i = field_names.index(c)
                name_convert[c] = '%s (%s)' % (c, fields[i][1])
        dataframe.rename(columns=name_convert, inplace=True)
        file_stream = StringIO.StringIO()
        dataframe.to_csv(file_stream, index=False)
        # , date_format = '%s' - not yet working in production pandas :-( 
        return file_stream.getvalue()
    
def smart_text(s, encoding='utf-8', errors='strict'):
    if isinstance(s, unicode):
        return s
    try:
        if not isinstance(s, basestring):
            if hasattr(s, '__unicode__'):
                s = s.__unicode__()
            else:
                s = unicode(bytes(s), encoding, errors)
        else:
            s = s.decode(encoding, errors)
    except UnicodeDecodeError as e:
        if not isinstance(s, Exception):
            raise e
        else:
            s = ' '.join([smart_text(arg, encoding, errors) for arg in s])
    return s

def super_smart_text(text):
    enc = chardet.detect(text)
    text = unicode(text, enc['encoding'], errors='replace')
    text = smart_text(text)
    text = text.encode('UTF8')
#     big_uni = re.compile(r'\\+u([0-9a-f][1-9a-f]|[1-9a-f][0-9a-f])[0-9a-f][0-9a-f]')
#     text = re.sub(big_uni, '', text)
    return text