import DbViewer.models as m
import DbViewer
from django.core.urlresolvers import reverse
import django.views.generic as generic
import settings, traceback
from django.core.urlresolvers import NoReverseMatch
# from django import forms
# from django.forms.formsets import formset_factory
# from django.db import models
from django.shortcuts import redirect
import json
from django.http import HttpResponse
import DbInspect
from datetime import datetime as dtdt
from django.core.cache import cache
from django import forms
from django.forms.models import modelform_factory
import django.views.generic.edit as generic_editor

TREE_CACHE_KEY = 'tree_data'
CACHE_KEEP_TIME = 3600



class ViewBase(object): #generic.TemplateView
    top_active = None
    
    def get(self, request, *args, **kw):
        self.setup_context(**kw)
        return super(ViewBase, self).get(request, *args, **kw)
    
    def setup_context(self, **kw):
        self._context = {}
        self._basic_context()
        
    def _basic_context(self):
        top_active = None
        if self.top_active is not None:
            self.request.session['top_active'] = self.top_active
        elif 'top_active' in self.request.session:
            top_active = self.request.session['top_active']
        if 'message' in self.request.session:
            self._context['info'] = self.request.session.pop('info')
        if 'success' in self.request.session:
            self._context['success'] = self.request.session.pop('success')
        if 'errors' in self.request.session:
            self._context['errors'] = self.request.session.pop('errors')
        self._context['base_template'] = 'page_base.html'
        raw_menu = []
        for item in DbViewer.TOP_MENU:
            raw_menu.append(item)
        if self.request.user.is_staff:
            raw_menu.append({'url': 'admin:index', 'name': 'Admin'})
        top_menu = []
        for item in raw_menu:
            try:
                menu_item = {'url': reverse(item['url']), 'name': item['name']}
            except NoReverseMatch:
                print 'No Reverse Match for "%s"' % item['url']
            else:
                if item['url'] == top_active:
                    menu_item['class'] = 'active'
                top_menu.append(menu_item)
        
        self._context['top_menu'] = top_menu
        self._context['site_title'] = settings.SITE_TITLE
    
class FilterChoice(forms.Form):
    def __init__(self, init_val, *args, **kwargs):
        super(FilterChoice, self).__init__(*args, **kwargs)
        choices = [(-1,'')] + [(f.id, str(f)) for f in m.Filter.objects.all()]
        self.fields['filters'] = forms.ChoiceField(choices=choices, initial=init_val, label='Choose existing Filter');

class Main(ViewBase, generic_editor.TemplateResponseMixin, generic_editor.ModelFormMixin, generic_editor.ProcessFormView):
    template_name = 'main_display.html'
    form_class = modelform_factory(m.Filter)
    sub_type = None
        
    def post(self, request, *args, **kw):
        self.setup_context(**kw)
        return super(Main, self).post(request, *args, **kw)
    
    def setup_context(self, **kw):
        super(Main, self).setup_context(**kw)
        fid, mfilter = -1, None
        if 'submit_type' in self.request.POST:
            self.sub_type = self.request.POST['submit_type']
        
        if 'filters' in self.request.POST and self.request.POST['filters'] != '-1':
            fid = int(self.request.POST['filters'])
            mfilter = m.Filter.objects.get(id=int(fid))
        self._set_mfilter(fid)
        self.object = mfilter

    def _set_mfilter(self, fid):
        self._context['choose_filter'] = FilterChoice(fid)
    
    def get_context_data(self, **kw):
        self._context.update(super(Main, self).get_context_data(**kw))
        return self._context
    
    def get_form_kwargs(self):
        kwargs = {}
        if self.sub_type == 'edit':
            kwargs = super(Main, self).get_form_kwargs()
        kwargs.update({'instance': self.object})
        return kwargs
    
    def form_valid(self, form):
        self.object = form.save()
        self._set_mfilter(self.object.id)
        tree = TreeGenerater()
        error = tree.execute_filter(self.object.code, self.object.db.id, str(self.object))
        self._context['filter_form_error'] = error
        return self.render_to_response(self.get_context_data(form=form))

    def form_invalid(self, form):
        if len(form.errors) > 0:
            self._context['filter_form_error'] = 'Database and code are both required'
        return self.render_to_response(self.get_context_data(form=form))
    
def clear_cache(request):
    cache.delete(TREE_CACHE_KEY)
    return redirect(reverse('main'))
    
def tree_json(request):
    tree = TreeGenerater()
    json = tree.json_data
    if 'node' in request.GET:
        json = tree.get_values(request.GET['node'])
    return HttpResponse(json, content_type="application/json")

class ContactForm(forms.Form):
    subject = forms.CharField(max_length=100)
    message = forms.CharField()
    sender = forms.EmailField()
    cc_myself = forms.BooleanField(required=False)

class TreeGenerater:
    _id = 0
    comms = None
    
    def __init__(self):
        if cache.has_key(TREE_CACHE_KEY):
            self.json_data = cache.get(TREE_CACHE_KEY)
            self._data = json.loads(self.json_data)
            self._id = self._get_max_id(self._data[-1])
        else:
            self._data = []
            for db in m.Database.objects.filter(live=True):
                self._data.append(self._get_db(db))
            self._generate_json()
            
    def _generate_json(self):
        self.json_data = json.dumps(self._data)
        cache.set(TREE_CACHE_KEY, self.json_data, CACHE_KEEP_TIME)
    
    def get_values(self, node_id):
        node_id = int(node_id)
        db_id, table = self._find_table(node_id)
        comms = self._get_comms(m.Database.objects.get(id=db_id))
        table_name = table['table_name']
        fields = [f[0] for f in table['fields']]
        rows = self._get_rows(comms.get_values(table_name), fields)
        table['children'] = rows
        if 'load_on_demand' in table:
            del table['load_on_demand']
        self._generate_json()
        return json.dumps(rows)
    
    def execute_filter(self, sql, db_id, filter_name):
        comms = self._get_comms(m.Database.objects.get(id=db_id))
        success, result, fields = comms.execute(sql)
        if success:
            rows = self._get_rows(result, fields)
            d = {'id': self._get_id(), 'label': 'FILTER: %s' % filter_name, 'children': rows}
            d['info'] = [('Filter Properties', [])]
            d['info'][0][1].append(('Results', len(rows)))
            d['info'][0][1].append(('SQL', sql))
            self._data.append(d)
            self._generate_json()
            return None
        else:
            return result
            
    def _get_rows(self, raw_rows, fields):
        rows = []
        for v, label in raw_rows:
            row = {'id': self._get_id(), 'label': label}
            row['info'] = [['', []]]
            row['info'][0][1] = [(name, val) for name, val in zip(fields, v)]
            rows.append(row)
        return rows
    
    def _find_table(self, node_id):
        for db_info in self._data:
            db_id = db_info['db_id']
            for table in db_info['children']:
                if table['id'] == node_id:
                    return db_id, table
    
    def _get_db(self, db):
        comms = self._get_comms(db)
        d = {'id': self._get_id(), 'label': 'DATABASE: %s' % db.name, 'db_id': db.id}
        d['info'] = [('Database Properties', [])]
        for name, value in db.conn_values():
            d['info'][0][1].append((name, value))
        d['info'][0][1].append(('Database Version', comms.get_version()))
        d['children'] = self._get_tables(comms, db)
        return d
    
    def _get_comms(self, db):
        if not self.comms:
            Comms = getattr(DbInspect, db.db_type.class_name)
            self.comms = Comms(dict(db.conn_values()))
        return self.comms
        
    def _get_tables(self, comms, db):
        t_data = []
        tables, prop_names = comms.get_tables()
        for t_name, t_info in tables:
            table = {'id': self._get_id(), 'label': t_name, 'table_name': t_name, 'load_on_demand': True}
            table['info'] = [('Table Properties', []), ('Fields', [])]
            for name, value in zip(prop_names, t_info):
                if type(value) == dtdt:
                    value = value.strftime(settings.CUSTOM_DT_FORMAT)
                table['info'][0][1].append((name, value))
            fields = comms.get_fields(t_name)
            table['info'][0][1].append(('Field Count', len(fields)))
            table['fields'] = fields
            for field in fields:
                table['info'][1][1].append((field[0], '[%s]' % str(field[1])))
            t_data.append(table)
        return t_data
            
    def _get_id(self):
        self._id += 1
        return self._id
    
    def _get_max_id(self, ob):
        if self._id != 0 or len(self._data) == 0:
            return 0
        if 'children' in ob:
            return self._get_max_id(ob['children'][-1])
        elif 'id' in ob:
            return ob['id']
        return 0










