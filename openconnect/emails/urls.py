from django.conf.urls.defaults import *
from django.contrib.auth.decorators import login_required
from django.views.generic.simple import direct_to_template
from django.views.generic.list_detail import object_list, object_detail
#from django.views.generic.create_update import create_object, update_object, delete_object
from emails.models import Email


urlpatterns = patterns('emails.views',
    url(r'^create/$', 'create_email', name='emails-create'),
    url(r'^list/draft/$', 'draft_list', name='emails-listdraft',
        kwargs = {'extra_context': {'title':'Drafts'}} ), 
    url(r'^update/(?P<object_id>.*)/$', 'update_email', name='emails-update',),
    url(r'^dumppost/$', 'dumppost', name='dumppost'),
    url(r'^unsubscribe/(?P<id>\d+)/$', 'unsubscribe', name='emails-unsubscribe',),
    url(r'^addrecipients/$', 'addrecipients', name="emails-addrecipients",),
    url(r'^fromsentmail/$', 'from_sent_mail', name="emails-selectcontactsfromsentmail",),
)

urlpatterns += patterns('django.views.generic.simple',
    url(r'^sent/', login_required(direct_to_template), {'template': 'emails/sent.html'}, name='emails-sent'),
)

urlpatterns += patterns('django.views.generic.list_detail',
    url(r'^list/template/$', login_required(object_list), name='emails-listtemplate', 
        kwargs={'queryset': Email.objects.filter(status__exact = "template").order_by("-last_edited"),
                'extra_context': {'title':'Templates'}} ),
    url(r'^list/sent/$', login_required(object_list), name='emails-listsent', 
        kwargs={'queryset': Email.objects.filter(status__exact = "sent mail").order_by("-last_edited"),
                'extra_context': {'title':'Sent mail'}} ),
    url(r'^detail/(?P<object_id>\d+)/$', login_required(object_detail), name='emails-detail', 
        kwargs={'queryset': Email.objects.all(), } ),
)

urlpatterns += patterns('django.views.generic.create_update',
    url(r'^delete/(?P<object_id>.*)/draft/$', 'delete_object', name='emails-delete-draft', 
        kwargs={'model': Email, 'post_delete_redirect': '/emails/list/draft/'} ),
    url(r'^delete/(?P<object_id>.*)/template/$', 'delete_object', name='emails-delete-template', 
        kwargs={'model': Email, 'post_delete_redirect': '/emails/list/template/'} )
)


#create email/template/draft
#update drafts
#update template
#delete drafts
#delete template
#list drafts
#list templates
#list sentmail
#detail drafts
#detail template
#detail sentmail
