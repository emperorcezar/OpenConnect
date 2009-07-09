from django.template import RequestContext
from django.shortcuts import get_object_or_404
from utils.render import render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.generic.list_detail import object_list
from django.db import models
from django.db.models import Q
from accounts.models import UserProfile
from contacts.forms import ImportContactFile, AddContact, BasicSearch
from contacts.models import Contact, ContactEditHistory, contactattrs, ContactSavedSearch
import csv, cStringIO, copy, re
from datetime import datetime
import tagging.utils as tagutils
from tagging.models import Tag, TaggedItem
from emails.models import Email
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType

def remove_tags(contacts, tag_list):
    tags = tagutils.get_tag_list(tag_list)
    ctype = ContentType.objects.get_for_model(Contact)

    tag_set = TaggedItem.objects.filter(tag__in = tags, object_id__in = [c.id for c in contacts], content_type = ctype)
    tag_set.delete()

def add_tags(contacts, tags):
    for contact in contacts:
        Tag.objects.add_tag(contact, tags)

@login_required
def savedsearch(request, id):
    return search(request, results=id)


@login_required
def selectemailrecipients(request):
    return search(request, results="results", rtemplate="contacts/results_back_to_email.html")

@login_required
def searchresults(request):
    return search(request, results="results")

@login_required
def check_contact(request, id):
    '''
    Ajax checkbox click. Switches the state of a contact.
    '''
    contacts = request.session.get('checked_contacts', [])

    if id in contacts:
        contacts.remove(int(id))
    else:
        contacts.append(int(id))

    request.session['checked_contacts'] = contacts

    return HttpResponse('')

@login_required
def search(request, results="new", page=1, paginate_by=10, rtemplate="contacts/results.html"):
    '''
    Search algorithm. Cululative. Each search is applied to the current grouping unless "New Search" is clicked.
    '''
    
    page = int(request.GET.get('page', request.session.get('searchpage', 1)))
    profile = getprofile(request.user)
    sortby = request.GET.get('sortby', request.session.get('sortby', ''))
    request.session['sortby'] = sortby
    paginate_by = int(request.POST.get('pagingprefs', profile.pagingprefs))
    
    if results == "new":    # This is the first hit on the search page, there's no contacts or post data to be presented.
        bform = BasicSearch()
        # add attributes
        context = locals().copy()
        context['contactattrs'] = contactattrs
        return render_to_response('contacts/search.html', context)

    if (request.method == "POST"):  # They've submitted a query, filter the contacts
        contacts = Contact.objects.all()    # Brand new search results
        request.session['checked_contacts'] = []

        if "searchtype" in request.POST:        # if they're performing a search of any kind, go back to page 1
            page = 1

        form = BasicSearch(request.POST)
        if form.is_valid():
            # filter contacts based on values in form
            if form.cleaned_data['first_name']:
                contacts = contacts.filter(first_name__search = form.cleaned_data['first_name'])
                
            if form.cleaned_data['last_name']:
                contacts = contacts.filter(last_name__search = form.cleaned_data['last_name'])

            if form.cleaned_data['email']:
                contacts = contacts.filter(email__search = '"'+form.cleaned_data['email']+'"')

            if form.cleaned_data['tags']:
                qstagquery = tagutils.get_tag_list(form.cleaned_data['tags'])
                taggedcontacts = TaggedItem.objects.get_by_model(Contact, [tag.name for tag in qstagquery])
                contacts = contacts.filter(id__in = [c.id for c in taggedcontacts])

        else:   # BasicSearch form is not valid
            bform = form
            return render_to_response('contacts/search.html', locals())

        # save search results in the session
        request.session['searchresults'] = contacts
        request.session['searchpage'] = page
        profile = getprofile(request.user)
        profile.pagingprefs = paginate_by
        profile.save()
        #request.session['pagingprefs'] = paginate_by
        # redirect to /contacts/search/results/
        #return HttpResponseRedirect('/contacts/search/results/')  # commented this out when updating this view for email recipient stuff.  It seems to work normally still.

    # request.method == "GET"
    if results == "results":
        # get the search result set from the session
        contacts = request.session.get('searchresults', [])
        cids = [c.id for c in contacts]
        qscontacts = Contact.objects.filter(id__in=cids)
    else:
        css = ContactSavedSearch.objects.get(pk=results)
        qscontacts = css.contact_list.all()
    if sortby != '':
        qscontacts = qscontacts.order_by(sortby)
    form = BasicSearch()
    sharedtags = getsharedtags(qscontacts)
    unsharedtags = [t.name for t in Tag.objects.exclude(name__in=sharedtags)]
    # render the results page

    checked_contacts = request.session.get('checked_contacts', [])

    print("%s" % (checked_contacts))

    return object_list(request, qscontacts, paginate_by=paginate_by, page=page, template_name=rtemplate, extra_context={"checked_contacts": checked_contacts, "bform":form, "contactattrs":contactattrs, "sharedtags":sharedtags, "unsharedtags":unsharedtags})
    #return render_to_response('contacts/results.html', context_instance=RequestContext(request, {"bform":form, "contacts":contacts}))


@login_required
def advanced_search(request):
    checked_contacts = request.session.get('checked_contacts', [])
    page = int(request.GET.get('page', request.session.get('searchpage', 1)))
    profile = getprofile(request.user)
    sortby = request.GET.get('sortby', request.session.get('sortby', ''))
    request.session['sortby'] = sortby
    paginate_by = int(request.POST.get('pagingprefs', profile.pagingprefs))
    
    if request.method == 'GET':
        session_contacts = request.session.get('searchresults', [])
        cids = [c.id for c in session_contacts]
        contacts = Contact.objects.filter(id__in=cids)
        sharedtags = getsharedtags(contacts)
        unsharedtags = [t.name for t in Tag.objects.exclude(name__in=sharedtags)]

        return object_list(request, contacts, paginate_by=paginate_by, page=page, template_name="contacts/advanced_search_page.html", extra_context={"checked_contacts": checked_contacts, "contactattrs":contactattrs, "sharedtags":sharedtags, "unsharedtags":unsharedtags, "request":request})

    else:
        if not request.POST.get('search', None) == 'New Search':
            session_contacts = request.session.get('searchresults', [])

            if len(session_contacts) > 0:
                cids = [c.id for c in session_contacts]
                contacts = Contact.objects.filter(id__in=cids)
                print("Cleaned contacts")
            else:
                contacts = Contact.objects.all()
                request.session['checked_contacts'] = []
        else:
            contacts = Contact.objects.all()
            request.session['checked_contacts'] = []

        attribute = request.POST.get('attribute', '')
        condition = request.POST.get('condition', '')
        query = request.POST.get('query', '')
        if request.POST.get('or', None):
            operator = 'or'
        else:
            operator = 'and'

        if attribute not in ('tag_list', 'full_name'):
            if condition == "contains":
                attrstr = "%s__%s" % (attribute, "icontains")
                q = Q( **{ str(attrstr) : str(query) } )
                
                print("Contains %s" %(query,))

            elif condition == "doesn't contain":
                attrstr = "%s__%s" % (attribute, "icontains")
                q = ~Q( **{ str(attrstr) : str(query) } )

                print("Doesn't Contain: %s" %(query,))

            elif condition == "is":
                attrstr = "%s__%s" % (attribute, "exact")
                q = Q( **{ str(attrstr) : str(query) } )

                print("Is %s" %(query,))
                                        
            elif condition == "is empty":
                attrstr = "%s__%s" % (attribute, "exact")
                query = ""
                q = Q( **{ str(attrstr) : str(query) } )

                query = None
                q = q | Q( **{ str(attrstr) : str(query) } )

                
                print("Is Empty")

            elif condition == "is not empty":
                attrstr = attribute
                q = ~Q( **{ str(attrstr) : "" } )
                q = q & ~Q( **{ str(attrstr) : None } )
               
                print("Is Not Empty")
                    

            if operator == 'and':
                contacts = contacts.filter(q)
                print("And")
                print(q)
            elif operator == 'or':
                print("Or")
                contacts = contacts | Contact.objects.filter(q)

        elif attribute == 'tag_list':
            print("Hit tags: " + condition)
            ctype = ContentType.objects.get_for_model(Contact)
            temp_contacts = []

            if condition == "contains":
                tags = Tag.objects.filter(name__contains = query.lower())
                print(str(attribute))

            elif condition == "doesn't contain":
                tags = Tag.objects.filter(name__contains = query)
                print("tags: " + str(tags))
                
            elif condition == "is":
                tags = Tag.objects.filter(name = query)
                    
            if condition == "is empty":
                temp_contacts = Contact.objects.exclude(id__in = [item.object_id for item in TaggedItem.objects.filter(content_type = ctype)])
            elif condition == "doesn't contain":
                temp_contacts = Contact.objects.exclude(id__in = [item.object_id for item in TaggedItem.objects.filter(tag__in = tags, content_type = ctype)])
            elif condition == "is not empty":
                temp_contacts = Contact.objects.filter(id__in = [item.object_id for item in TaggedItem.objects.filter(content_type = ctype)])
            else:
                temp_contacts = Contact.objects.filter(id__in = [item.object_id for item in TaggedItem.objects.filter(tag__in = tags, content_type = ctype)])

            if operator == 'or':
                contacts = contacts | temp_contacts
            else:
                contacts = contacts & temp_contacts

        elif attribute == 'full_name':
            first_name = query.rsplit(' ', 1)[0]
            last_name = query.rsplit(' ', 1)[-1]

            if condition == "contains":
                attrstr = "first_name__%s" % ("icontains",)
                q = Q( **{ str(attrstr) : str(first_name) } )

                if len(query.rsplit(' ', 1)) > 1:
                    attrstr = "last_name__%s" % ("icontains",)
                    q = q & Q( **{ str(attrstr) : str(last_name) } )
                
                print("Contains %s" %(query,))

            elif condition == "doesn't contain":
                attrstr = "first_name__%s" % ("icontains",)
                q = Q( **{ str(attrstr) : str(first_name) } )

                if len(query.rsplit(' ', 1)) > 1:
                    attrstr = "last_name__%s" % ("icontains",)
                    q = q & Q( **{ str(attrstr) : str(last_name) } )

                q = ~q

                print("Doesn't Contain: %s" %(query,))

            elif condition == "is":
                attrstr = "first_name__%s" % ("exact",)
                q = Q( **{ str(attrstr) : str(first_name) } )

                if len(query.rsplit(' ', 1)) > 1:
                    attrstr = "last_name__%s" % ("exact",)
                    q = q & Q( **{ str(attrstr) : str(last_name) } )

                print("Is %s" %(query,))
                                        
            elif condition == "is empty":
                attrstr = "first_name__%s" % ("exact",)
                q = Q( **{ str(attrstr) : "" } )

                if len(query.rsplit(' ', 1)) > 1:
                    attrstr = "last_name__%s" % ("exact",)
                    q = q & Q( **{ str(attrstr) : "" } )
                
                print("Is Empty")

            elif condition == "is not empty":
                attrstr = "first_name__%s" % ("exact",)
                q = ~Q( **{ str(attrstr) : "" } )

                if len(query.rsplit(' ', 1)) > 1:
                    attrstr = "last_name__%s" % ("exact",)
                    q = q & ~Q( **{ str(attrstr) : "" } )
                
                print("Is Not Empty")

            if operator == 'and':
                contacts = contacts.filter(q)
                print("And")
                print(q)
            elif operator == 'or':
                print("Or")
                contacts = contacts | Contact.objects.filter(q)

            
        # save search results in the session
        request.session['searchresults'] = contacts
        request.session['searchpage'] = page
        profile = getprofile(request.user)
        profile.pagingprefs = paginate_by
        profile.save()

        sharedtags = getsharedtags(contacts)
        unsharedtags = [t.name for t in Tag.objects.exclude(name__in=sharedtags)]
        return object_list(request, contacts, paginate_by=paginate_by, page=page, template_name='contacts/advanced_search_page.html', extra_context={"checked_contacts": checked_contacts, "contactattrs":contactattrs, "sharedtags":sharedtags, "unsharedtags":unsharedtags, "request":request})


@login_required
def add(request):
    # initialize session data
    request.session['newcontacts'] = []
    request.session['newcontactscsv'] = []
    request.session['existingcontacts'] = []
    request.session['existingcontactscsv'] = []
    request.session['badcontacts'] = []
    request.session['badcontactscsv'] = []

    if (request.method == "POST"):
        form = AddContact(request.POST)
        if form.is_valid():
            # add the contact and redirect to /contacts/new
            line = copy.deepcopy(form.cleaned_data)
            savecontact(request, form, line)
            return HttpResponseRedirect('/contacts/new/')
    else:
        form = AddContact()
    return render_to_response('contacts/add.html', locals())


@login_required
def import_from_file(request):
    # XXX column names need to be documented!  This is a user interface component.
    # initialize session data
    request.session['newcontacts'] = []
    request.session['newcontactscsv'] = []
    request.session['existingcontacts'] = []
    request.session['existingcontactscsv'] = []
    request.session['badcontacts'] = []
    request.session['badcontactscsv'] = []

    if request.method == "POST":
        form = ImportContactFile(request.POST, request.FILES)
        if form.is_valid():
            # parse file and add contacts, then redirect to /contacts/new
            r = csv.DictReader(cStringIO.StringIO(request.FILES['file'].read()))
            for line in r:
                # Create a contact record with this data.
                cform = AddContact(line)
                savecontact(request, cform, line)
            return HttpResponseRedirect('/contacts/new/')
    else:
        form = ImportContactFile()
    return render_to_response('contacts/import.html', locals())


@login_required
def new(request):
    newcontacts = request.session.get('newcontacts', [])
    existingcontacts = request.session.get('existingcontacts', [])
    badcontacts = request.session.get('badcontacts', [])
    return render_to_response('contacts/new.html', locals())


@login_required
def contactdetails(request, id):
    contact = Contact.objects.get(id=id)
    cdata = []
    for f in Contact._meta.fields:
        if f.verbose_name != "ID" and f.name != "token":
            cdata = cdata + [(f.verbose_name, f.value_from_object(contact))]
    cdata.insert(3 ,('Tags', contact.tag_list))
    chistory = ContactEditHistory.objects.filter(contact=contact)
    return render_to_response('contacts/detail.html', locals())


@login_required
def editcontact(request, id):
    contact = Contact.objects.get(id=id)  # re-get the contact from the db to make sure it's the current data.
    if request.method == "POST":
        form = AddContact(request.POST, instance=contact)
        if form.is_valid():
            # TODO: If state is set and nothing else in the address is set, set the state blank.
            # Update the contact
            contact = form.save()
            # log it in the history
            contacteditlog(request, contact, "Contact updated.")
            # return to this form, or to the search results.
            if request.POST['submit'] == "Save and close":
                return HttpResponseRedirect("/contacts/search/results")
            # else, return to this form (meaning, render it as if it hadn't been a post, but with error messages)
    else:  # request.method == GET
        form = AddContact(instance=contact)
    cform = form
    return render_to_response('contacts/edit.html', locals())
    


@login_required
def deletecontact(request, id):
    contact = Contact.objects.get(id__exact=id)
    if request.method == "POST":
        if request.POST['submit'] == "Yes, delete the contact":
            # delete the contact and their history.
            ch = ContactEditHistory.objects.filter(contact=contact)
            for item in ch:
                item.delete()
            contact.delete()
            return HttpResponseRedirect('/contacts/search/results/')
        else:
            # This post is not from the confirm page, or they didn't click the confirm button. 
            return HttpResponseRedirect('/contacts/edit/%d' % (contact.id))
    else:
        # display the confirmation page
        return render_to_response('contacts/delete_confirm.html', locals())


@login_required
def nextaction(request):
    if request.method == "POST":
        contacts = request.session.get('searchresults', [])
        if request.POST['nextaction'] == "newtag":
            add_tags(contacts, request.POST['param'])
        elif request.POST['nextaction'][0:3] == "add":
            add_tags(contacts, request.POST['param'])
        elif request.POST['nextaction'][0:6] == "remove":
            remove_tags(contacts, request.POST['param'])
        elif request.POST['nextaction'] == "savesearch":
            search = ContactSavedSearch(user=request.user, name=request.POST['param'], event_date=datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S"))
            search.save()
            for c in contacts:
                search.contact_list.add(c)
            search.save()
        elif request.POST['nextaction'] == "sendemail":
            e = Email.objects.create(subject="(New Email)", user=request.user, status="draft")
            for c in contacts:
                e.recipients.add(c)
            e.save()
            return HttpResponseRedirect('/emails/update/%d' % e.id)

        request.session['searchresults'] = contacts

        if request.POST['nextaction'] == "selectcontacts":
            checked_contacts = request.session.get('checked_contacts', [])

            contacts = contacts.filter(id__in = checked_contacts)
            request.session['searchresults'] = contacts
            request.session['checked_contacts'] = []

            return HttpResponseRedirect('/contacts/search/results/')

        if request.POST['nextaction'] == "selectcontactsadv":
            checked_contacts = request.session.get('checked_contacts', [])

            contacts = contacts.filter(id__in = checked_contacts)
            request.session['searchresults'] = contacts
            request.session['checked_contacts'] = []
            return HttpResponseRedirect('/contacts/search/advanced/')


    return HttpResponseRedirect('/contacts/search/results/?page=%s' % (request.GET['page']))




### helper functions

def saveinsession(request, setname, data):
    """
    Adds a data list to a dataset in the current user's session.

    arguments:
        *request* - The request object
        *setname* - The name of the session variable to add the data to
        *data* - A list of data to add to the session variable

    return:
        none
    """
    dataset = request.session.get(setname, [])
    if type(data) == type([]):
        request.session[setname] = dataset + data
    else:
        request.session[setname] = dataset + [data]


def savecontact(request, form, line):
    """
    Saves the data from an AddContact form to the database and stores it in 
    the session variable.

    arguments:
        *request* - The request object
        *form* - The form of data to save
        *line* - The original data as submitted

    return:
        none
    """
    # Create a contact record with this data.
    if form.is_valid():
        c = form.save(commit=False)

        # Check if the email is already in the db.  If so, put it on the 
        #   existing contact list.
        try:
            if form.cleaned_data['email'] not in ('', None):
                existing = Contact.objects.get(email__exact = form.cleaned_data['email'])

            existing = Contact.objects.get(first_name = form.cleaned_data['first_name'], last_name = form.cleaned_data['last_name'])
            saveinsession(request, "existingcontacts", c)
            saveinsession(request, "existingcontactscsv", [line])
        except Contact.DoesNotExist:
            # The data is valid and the email is unique.  Save this contact i
            #   as new.
            c = form.save()
            saveinsession(request, "newcontacts", c)
            saveinsession(request, "newcontactscsv", [line])
            # Create a contact history record for this event
            contacteditlog(request, c, "Contact created.")
            
    else:
        # Form didn't validate.  Must have invalid or missing data.
        # format the error string for printing
        errors = ""
        for k in form.errors.iterkeys():
            errors += "%s: %s" % (k,form.errors[k]) # XXX: For some reason, the value is still in html.  It shouldn't be.
        line.update({'notes': errors})
        saveinsession(request, "badcontacts", [line]) 
        saveinsession(request, "badcontactscsv", [line])


def contacteditlog(request, contact, message):
    """
    Adds a record to the contact's edit history.

    arguments:
        *request* - The request object
        *contact* - The contact being edited
        *message* - A description of what happened

    return:
        none
    """
    hist = ContactEditHistory(user=request.user,
                       contact=contact,
                       event_date=datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S"),
                       message=message)
    hist.save()


def getprofile(user):
    '''
    Get the user profile, and if it's not there make it.

    arguments:
        *request* - The request object

    return:
        The logged in user's profile
    '''
    try:
        profile = user.get_profile()
    except UserProfile.DoesNotExist:
        profile = UserProfile(user=user, pagingprefs=10)
        profile.save()
    return profile


def getsharedtags(contacts):
    '''
    Get the tags shared among the contacts in "contacts"

    arguments:
        *contacts* - A queryset of Contact objects

    return:
        A list of tags shared among all these contacts
    '''
    tags = {}
    total = contacts.count()
    sharedtags = []
    for c in contacts:
        for tag in c.tags:
            tags[tag.name] = tags.get(tag.name, 0) + 1
    for tag, count in tags.items():
        if count == total:
            sharedtags.append(tag)
    return sharedtags

@login_required
def events(request, id):
    contact = get_object_or_404(Contact, pk=id)
    events = contact.registrant_set.all()
    return render_to_response('contacts/events.html', locals())

@login_required
def tag_search(request, tag, page=1, paginate_by=10, rtemplate="contacts/tag_results.html"):
    qstagquery = tagutils.get_tag_list(tag)
    taggedcontacts = TaggedItem.objects.get_by_model(Contact, [tag.name for tag in qstagquery])
    qscontacts = Contact.objects.filter(id__in = [c.id for c in taggedcontacts])
    request.session['searchresults'] = qscontacts

    return HttpResponseRedirect(reverse('contacts-searchresults'))
