import re
import chardet

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