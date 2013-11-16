from django.conf.urls import patterns, include, url
import DbViewer.views

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', DbViewer.views.Main.as_view(), name='main'),
    url(r'^clear_cache$', DbViewer.views.clear_cache, name='clear_cache'),
    url(r'^tree.json$', DbViewer.views.tree_json, name='tree_json'),
    url(r'^export$', DbViewer.views.Export.as_view(), name='export'),
    url(r'^generate_csv_zip', DbViewer.views.generate_csv_zip, name='generate_csv_zip'),
    url(r'^graph$', DbViewer.views.Graph.as_view(), name='graph'),
    url(r'^graphpop$', DbViewer.views.Graph.as_view(), name='graphpop'),

    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
