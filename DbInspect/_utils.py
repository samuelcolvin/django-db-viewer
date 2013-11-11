MAX_ROWS = 1000
SIMPLE_LIMIT = 50
from django.utils.encoding import smart_text

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