from django.conf.urls.defaults import *
from django.conf import settings
import accounts, main
import openconnect.settings
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/(.*)', admin.site.root),
)



urlpatterns += patterns(
    '',
    url(r'^$', 'main.views.index'),
    url(r'^taglist.json$', 'main.views.json_tag_list', name="json-tag-list"),
    url(r'^csv/(?P<setname>.*)/$', 'main.views.exportcsv', name="getcsv"),
    url(r'^pdf/(?P<setname>.*)/$', 'main.views.exportpdf', name="getpdf"),
    url(r'^accounts/', include('accounts.urls')),
    url(r'^contacts/', include('contacts.urls')),
    url(r'^contacts/$', 'contacts.views.search', name='contacts'),
    url(r'^emails/', include('emails.urls')),
    url(r'^reports/', include('reports.urls')),
    url(r'^tagging/', include('mytags.urls')),
    url(r'^events/', include('events.urls')),
   

)

if settings.DEBUG:
     print "here"
     urlpatterns += patterns('',
          url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': openconnect.settings.MEDIA_ROOT, 'show_indexes': True}),
          )
