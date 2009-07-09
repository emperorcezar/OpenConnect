import os, sys
from django.template import RequestContext
from utils.render import render_to_response
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.views.generic.list_detail import object_list, object_detail
from django.views.generic.create_update import create_object, update_object, delete_object
from django.views.generic.simple import direct_to_template
from emails.models import Email
from emails.forms import CreateEmail
from contacts.models import Contact, ContactEditHistory, ContactSavedSearch

@login_required
def create_email(request):
    savedsearches = ContactSavedSearch.objects.filter(user=request.user).order_by("-event_date")
    if request.method == "POST":
        form = CreateEmail(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            url = '/emails/update/%d'
            status = ""
            if request.POST['Submit'] == "Save as draft":
                status = "draft"
            elif request.POST['Submit'] == "Save as template":
                status = "template"
            elif request.POST['Submit'] == "Send":
                status = "sent mail"
                url = '/emails/sent/'
            else:
                print "in apps/emails/views.py>create_email.  Template has changed" +\
                      " and view has not been updated.  You getting database errors?"
            e = form.save(extra_attrs={'user': request.user, 'status': status})
            if request.POST['Submit'] == "Send":
                send_email(e)
                return HttpResponseRedirect(url)
            return HttpResponseRedirect(url % e.id)
    else:
        # Check if an event was stuck in the get from the invite interface
        event = request.GET.get('event', None)
        form = CreateEmail(user=request.user)
    return render_to_response('emails/email_form.html', locals())


@login_required
def draft_list(*args, **kwargs):
    # this line depends on request being args[0], which it should be.
    kwargs['queryset'] = Email.objects.filter(status__exact = "draft").filter(user=args[0].user).order_by("-last_edited")
    return object_list(*args, **kwargs) 


@login_required
def update_email(request, object_id):
    email = Email.objects.get(pk=object_id)
    extra_attrs = {}
    if request.method == "POST":
        request.session['lasteditedemail'] = 0

        if "draft" in request.POST['Submit']:
            if email.status == "draft":
                # update the email
                form = CreateEmail(request.POST, request.FILES, instance=email, user=request.user)
                if form.is_valid():
                    form.save()
                    return HttpResponseRedirect('/emails/list/draft/')
            else:
                # create new email from form as "draft"
                form = CreateEmail(request.POST, request.FILES, user=request.user)
                if form.is_valid():
                    extra_attrs['status'] = "draft"
                    extra_attrs['user'] = request.user
                    new_email = form.save(extra_attrs=extra_attrs)
                    # Copy recipients
                    for contact in email.recipients.all():
                        new_email.recipients.add(contact)

                    return HttpResponseRedirect('/emails/list/draft/')

        elif "template" in request.POST['Submit']:
            # If it's a sent mail make a new template, else just turn it into a template
            if email.status == "sent mail":
                form = CreateEmail(request.POST, request.FILES, user=request.user)
            else:
                form = CreateEmail(request.POST, request.FILES, instance=email, user=request.user)

            if form.is_valid():
                # change the status to "template"
                extra_attrs['status'] = "template"
                extra_attrs['user'] = request.user

                new_email = form.save(extra_attrs=extra_attrs)
                                # If new copy recipients
                if email.id != new_email.id:
                    for contact in email.recipients.all():
                        new_email.recipients.add(contact)

                return HttpResponseRedirect('/emails/list/template/')
        elif "Send" in request.POST['Submit']:
            # update the email
            if email.status == 'draft':
                form = CreateEmail(request.POST, request.FILES, instance=email, user=request.user)
            else:
                form = CreateEmail(request.POST, request.FILES, user=request.user)

            if form.is_valid():
                # change the status to "sent mail"
                extra_attrs['status'] = "sent mail"
                extra_attrs['user'] = request.user
                new_email = form.save(extra_attrs=extra_attrs)
                
                # If new copy recipients and attachment
                if email.id != new_email.id:
                    for contact in email.recipients.all():
                        new_email.recipients.add(contact)

                    if new_email.attachment in (None, ''):
                        new_email.attachment = email.attachment
                        print "attachment copied: %s" % (email.attachment,)
                        new_email.save()
                # send the email
                send_email(new_email)
                return HttpResponseRedirect('/emails/sent/')

    elif request.method == "GET":
        request.session['lasteditedemail'] = email.id
        form = CreateEmail(instance=email, user=request.user)


    savedsearches = ContactSavedSearch.objects.filter(user=request.user).order_by("-event_date")
    atchfilename = email.attachment.name.split("/")[-1]

    return render_to_response('emails/email_form.html',locals())
    
def unsubscribe(request, id):
    c = Contact.objects.get(id=id)
    if request.GET.get('confirm', None):
        c.do_not_email = True
        c.save()
        ch = ContactEditHistory(contact=c, message="The contact has unsubscribed.")
        ch.save()
        return direct_to_template(request, template="emails/unsubscribe.html")

    else:
        return direct_to_template(request, extra_context = locals(), template="emails/unsubscribe_confirm.html")
        

@login_required
def addrecipients(request):
    # if coming from email editing page
    if request.method == "POST":    # coming from email edit page
        # see if the email id is in the hidden input
        id = request.POST.get("emailid", "-9999")
        if id == "-9999":
            # check if latest draft has the same subject
            try:
                e = Email.objects.all().order_by('-last_edited')[0]
                if e.subject != request.POST['subject']:
                    raise IndexError
            except IndexError:
                # create the new draft and save that id in the session
                e = Email.objects.create(subject = request.POST['subject'], \
                                         user = request.user, \
                                         status = "draft", \
                                         message = request.POST.get('message', ''))  # there's a js check before we get here to ensure that subject exists in the post.
            id = e.id
        # save the email id in the session
        request.session['lasteditedemail'] = id
        # send the user to the special contact search page
        return HttpResponseRedirect('/contacts/search/emailrecipients/')
    elif request.method=="GET":  # coming from the search results page
        # get email id from session
        id = request.session.get("lasteditedemail", "-9999")
        if id != "-9999":
            e = Email.objects.get(id=id)

            # Clear recipients and set to search results
            for c in e.recipients.all():
                e.recipients.remove(c)
            
            # get recipient list from session
            for c in request.session.get("searchresults", []):
            # assign recipients to email
                if c.do_not_email == 0:
                    e.recipients.add(c)
            e.save()
            # redirect to email edit page
            return HttpResponseRedirect('/emails/update/%d/' % e.id)
        else:   # something went wrong, why is there no id?
            return HttpResponseRedirect('/emails/list/draft/')



@login_required
def from_sent_mail(request):
    if request.method == "POST":
        # see if the email id is in the hidden input
        id = request.POST.get("emailid", "-9999")
        if id != "-9999":
            clist = []
            e = Email.objects.get(id=id)
            for c in e.recipients.all():
                clist = clist + [c]
            request.session['searchresults'] = clist
        else:
            request.session['searchresults'] = []
    return HttpResponseRedirect('/contacts/search/results/')



##### Helper functions #####

def send_email(e):
    """
    send_email - spawns a child process to actually send emails.  The child take many minutes to execute, so it can't happen in a view directly.

    arguments:
        e - An email to be sent

    return:
        Nothing
    """
    import subprocess
    from django.conf import settings

    env = os.environ
    env['PYTHON_PATH'] = settings.SETTINGS_DIRECTORY+'/:'+settings.SETTINGS_DIRECTORY+'/../'
    env['DJANGO_SETTINGS_MODULE'] = 'settings'

   
    emailer = subprocess.Popen([settings.PYTHON_PROCESS, settings.EMAIL_SCRIPT_PATH, str(e.id)], env=env, stdout=sys.stdout, stderr=sys.stdout)



def dumppost(request):
    post = request.POST
    return render_to_response('dumppost.html', locals())
