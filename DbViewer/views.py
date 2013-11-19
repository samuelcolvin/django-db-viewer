from DbViewer.main_page import Main, clear_cache, tree_json
from django.core.urlresolvers import reverse
import DbViewer.models as m
import django.views.generic as generic
import DbViewer.views_base as views_base
from django.http import HttpResponse
import StringIO
import zipfile
import json

def _csvstr(request):
    qid = int(request.GET['queries'])
    query = m.Query.objects.get(id = qid)
    comms = query.db.get_comms()
    csvstr = comms.generate_string(query.code)
    return csvstr, query

def generate_csv_zip(request):
    csvstr, query = _csvstr(request)
    zip_mem = StringIO.StringIO()
    zipf = zipfile.ZipFile(zip_mem, 'a', zipfile.ZIP_DEFLATED)
    file_name = 'export_%s.csv' % str(query)
    zipf.writestr(file_name, csvstr)
    zipf.close()
    zip_mem.seek(0)
    response = HttpResponse(zip_mem, mimetype='application/zip')
    response['Content-Disposition'] = 'attachment; filename="%s.zip"' % file_name
    return response

def generate_csv(request):
    csvstr, _ = _csvstr(request)
    response = HttpResponse(csvstr, mimetype='text/plain')
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
        self._context['title'] = 'Graph'
        self._context['choose_query'] = views_base.FilterChoice(-1)
        f = ('id', 'name')
        queries = m.Query.objects.all().values_list(*f)
        queries = [dict(zip(f, v)) for v in queries]
        self._context['code_formats'] = json.dumps(queries)
        if 'pop' in self.request.path:
            self._context['base_template'] = 'pop_base.html'
        return self._context