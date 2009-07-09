from django.conf.urls.defaults import *
from django.contrib.auth.views import login, logout

urlpatterns = patterns('',
    url(r'^login/$',	'django.contrib.auth.views.login', name='accounts-login'),
    url(r'^logout/$',	'django.contrib.auth.views.logout_then_login', name='accounts-logout'),
)
