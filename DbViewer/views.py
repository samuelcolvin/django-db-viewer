from DbViewer.main_page import Main, clear_cache, tree_json
from django.core.urlresolvers import reverse
import DbInspect
import DbViewer.models as m
import django.views.generic as generic
import DbViewer.views_base as views_base
from django.http import HttpResponse
import StringIO
import zipfile

def generate_csv(request):
    qid = int(request.GET['queries'])
    query = m.Query.objects.get(id = qid)
    Comms = getattr(DbInspect, query.db.db_type.class_name)
    comms = Comms(dict(query.db.conn_values()))
    stream = comms.generate_csv(query.code)
    zip_mem = StringIO.StringIO()
    zipf = zipfile.ZipFile(zip_mem, 'a', zipfile.ZIP_DEFLATED)
    file_name = 'export_%s.csv' % str(query)
    zipf.writestr(file_name, stream.getvalue())
    zipf.close()
    zip_mem.seek(0)
    response = HttpResponse(zip_mem, mimetype='application/zip')
    response['Content-Disposition'] = 'attachment; filename="%s.zip"' % file_name
    return response

class Export(views_base.ViewBase, generic.TemplateView):
    template_name = 'export.html'
    top_active = 'export'
    
    def get_context_data(self, **kw):
        self._context.update(super(Export, self).get_context_data(**kw))
        self._context['choose_query'] = views_base.FilterChoice(-1)
        return self._context

class Graph(views_base.ViewBase, generic.TemplateView):
    template_name = 'graph.html'
    top_active = 'graph'
    
    def get_context_data(self, **kw):
        self._context.update(super(Graph, self).get_context_data(**kw))
        if 'pop' in self.request.path:
            self._context['base_template'] = 'pop_base.html'
        return self._context