from django.conf.urls.defaults import *

urlpatterns = patterns('reports.views',
    url(r'^create/$', 'create', name='reports-create'),
    url(r'^list/$', 'list', name='reports-list'),
    url(r'^display/(?P<id>.*)/$', 'display', name='reports-display'),
    url(r'^delete/(?P<id>.*)/$', 'deletereport', name='reports-delete'),
)
