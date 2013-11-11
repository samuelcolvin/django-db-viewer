from DbViewer.main_page import Main, clear_cache, tree_json
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
import DbInspect
import DbViewer.models as m

def generate_csv(request, qid = None):
    query = m.Query.objects.get(id = qid)
    Comms = getattr(DbInspect, query.db.db_type.class_name)
    comms = Comms(dict(query.db.conn_values()))
    comms.generate_csv(query.code)
    return redirect(reverse('main'))