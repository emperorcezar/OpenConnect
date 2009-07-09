from django.conf.urls.defaults import *

urlpatterns = patterns('contacts.views',
    url(r'^search/$', 'search', name='contacts-search'),
    url(r'^search/advanced/$', 'advanced_search', name='advanced-search'),
    url(r'^search/tag/(?P<tag>.*)/$', 'tag_search', name='contacts-tag-search'),
    url(r'^search/results/$', 'searchresults', name='contacts-searchresults'),
    url(r'^search/emailrecipients/$', 'selectemailrecipients', name='contacts-emailrecipients'),
    url(r'^search/saved/(?P<id>.*)/$', 'savedsearch', name='contacts-savedsearch'),
    url(r'^add/$', 'add', name='contacts-add'),
    url(r'^import/$', 'import_from_file', name='contacts-import'),
    url(r'^new/$', 'new', name='contacts-new'),
    url(r'^details/(?P<id>.*)/$', 'contactdetails', name='contacts-details'),
    url(r'^edit/(?P<id>.*)/$', 'editcontact', name='contacts-edit'),
    url(r'^delete/(?P<id>.*)/$', 'deletecontact', name='contacts-delete'),
    url(r'^search/action/$', 'nextaction', name='contacts-searchaction'),
    url(r'^(?P<id>.*)/events/$', 'events', name='registered-events'),
    url(r'^(?P<id>.*)/check/$', 'check_contact', name='contact-check'),

)
