from django.conf.urls import patterns, include, url
import DbViewer.views

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', DbViewer.views.Main.as_view(), name='main'),
    url(r'^clear_cache$', DbViewer.views.clear_cache, name='clear_cache'),
    url(r'^tree.json$', DbViewer.views.tree_json, name='tree_json'),
    url(r'^generate_csv/(?P<qid>\d+)$', DbViewer.views.generate_csv, name='generate_csv'),

    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
