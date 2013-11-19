import re
import chardet
import StringIO
import numpy

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
    
    def _sanitize_df(self, dataframe):
        for c in dataframe.columns:
            if dataframe[c].dtype == object:
                dataframe[c] = dataframe[c].apply(super_smart_text)
            # this doesn't seem to work :-( :
#             elif dataframe[c].dtype == numpy.int64:
#                 dataframe[c] = dataframe[c].astype(int)
        return dataframe

    def _to_string(self, dataframe, code, string_format='csv'):
        fields = self.get_query_fields(code)
        field_names = [f[0] for f in fields]
        name_convert = {}
        for c in dataframe.columns:
            if c in field_names and string_format == 'csv':
                i = field_names.index(c)
                col_type = fields[i][1]
                name_convert[c] = '%s (%s)' % (c, col_type)
                if col_type == 'DATETIME':
                    dataframe[c] = dataframe[c].apply(lambda x: x.strftime('%s'))
        dataframe.rename(columns=name_convert, inplace=True)
        file_stream = StringIO.StringIO()
        # , date_format = '%s' - not yet working in production pandas :-(
        if string_format == 'csv':
            dataframe.to_csv(file_stream, index=False)
        elif string_format == 'json':
            dataframe.to_json(file_stream, orient='records')
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
            print s
            import pdb; pdb.set_trace()
            raise e
        else:
            s = ' '.join([smart_text(arg, encoding, errors) for arg in s])
    return s

ALLOWED_ENCODING = set(['ascii', 'ISO-8859-2', 'windows-1252', 'SHIFT_JIS', 'Big5', 'IBM855', 'windows-1251', 'ISO-8859-5', 'KOI8-R', 'ISO-8859-7', 'EUC-JP', 'ISO-8859-8', 'IBM866', 'MacCyrillic', 'windows-1255', 'GB2312', 'EUC-KR', 'TIS-620'])
ESC_BYTES = re.compile(r'\\x[0-9a-f][0-9a-f]')
def super_smart_text(text):
    if text is None:
        return ''
    enc = chardet.detect(text)
    if enc['encoding'] is not None and enc['encoding'] in ALLOWED_ENCODING:
        text = unicode(text, enc['encoding'], errors='replace')
    else:
        text = ESC_BYTES.sub('', text.encode('string-escape'))
#     text = text.encode('UTF8')
    return text