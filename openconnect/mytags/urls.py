from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^manage/$', 'mytags.views.manage', name='mytags-manage'),
    url(r'^rename/(?P<tagname>.*)/$', 'mytags.views.rename', name='mytags-rename'),
    url(r'^remove/(?P<tagname>.*)/$', 'mytags.views.remove', name='mytags-remove'),
)
