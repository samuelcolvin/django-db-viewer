import DbViewer
from django.core.urlresolvers import reverse
from django.core.urlresolvers import NoReverseMatch
import settings
from django import forms
import DbViewer.models as m
    
class FilterChoice(forms.Form):
    def __init__(self, init_val, *args, **kwargs):
        super(FilterChoice, self).__init__(*args, **kwargs)
        choices = [(-1,'')] + [(f.id, str(f)) for f in m.Query.objects.all()]
        self.fields['queries'] = forms.ChoiceField(choices=choices, initial=init_val, label='Queries:');

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