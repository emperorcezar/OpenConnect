from django.conf.urls.defaults import *
from events.models import Event
from django.views.generic.list_detail import object_list
from django.views.generic.list_detail import object_detail


urlpatterns = patterns(
    'events.views',
    url(r'^add/$', 'add', name='event-add'),
    url(r'^search/$', 'search', name='event-search'),
    url(r'^search/execute.json$', 'execute_search', name='execute-search'),

    ## url(r'^details/(?P<id>.*)/$', 'event_details', name='events-details'),
    url(r'^edit/(?P<id>\d+)/$', 'edit', name='event-edit'),
    url(r'^registrants_status/(?P<id>.*)/$', 'registrants_pending_status',
        name='registrants_pending_status'),
    url(r'^invite/(?P<id>\d+)/$', 'invite', name='event-invite'),
    url(r'^emails/(?P<id>\d+)/$', 'emails', name='event-emails'),
    url(r'^pending_toggle/$', 'pending_toggle', name='pending_toggle'),
    url(r'^pricing_add/$', 'pricing_add', name='events-pricing-add'),
    url(r'^pricing_delete/$', 'pricing_delete', name='events-pricing-delete'),
    url(r'^delete/(?P<id>\d+)/$', 'delete', name='events-delete'),
    url(r'^details/(?P<slug>[\w-]+)/$', 'event_show', name='event-show'),
    url(r'^(?P<slug>[\w-]+)/register/$', 'register', name='event-register'),
    url(r'^(?P<slug>[\w-]+)/email_register/$', 'email_register', name='event-email-register'),
    url(r'^(?P<slug>[\w-]+)/register/(?P<token>[0-9a-f]{5,40})/$', 'token_register', name='event-register-token'),

    ## url(r'^search/action/$', 'nextaction', name='events-searchaction'),
    url(r'^$', object_list, {'queryset': Event.objects.all(),
                             'template_name': 'events_list.html'},
        name = 'events'),
    url(r'^(?P<object_id>\d+)/$', object_detail, {'queryset': Event.objects.all(),
                             'template_name': 'event_details.html'},
        name = 'event-list'),
    
)
