from django.template import RequestContext
from utils.render import render_to_response
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.db.models import Q
from reports.models import Report, SearchTerms
from reports.forms import CreateReport
from contacts.models import contactattrs, Contact
from django.contrib.contenttypes.models import ContentType
from tagging.models import Tag, TaggedItem



@login_required
def create(request):
    if request.method == "POST":
        form = CreateReport(request.POST)
        if form.is_valid():     # else is dropping through to the render_to_resposne
            r = form.save()
            # process advanced search here too
            contacts = Contact.objects.all()
            attribute = request.POST.getlist('attribute')
            condition = request.POST.getlist('condition')
            query = request.POST.getlist('query')
            operator = request.POST.getlist('operator')
            for i in xrange(0, len(attribute)):
                s = SearchTerms(field=attribute[i], 
                                condition=condition[i],
                                query=query[i],
                                order=i,
                                report=r)

                if i > 0:
                    try:
                        s.operator = operator[i-1]
                    except IndexError:
                        s.operator = 'and'
                else:
                    print("Default And %s" % (i,))
                    s.operator = 'and'
                    
                s.save()
                r.searchterms.add(s)
            r.save()
            return HttpResponseRedirect('/reports/display/%s' % r.id)
    else:
        form = CreateReport()

    context = locals().copy()
    context['contactattrs'] = contactattrs
    return render_to_response('reports/create.html', context)


@login_required
def list(request):
    reports = Report.objects.all()
    return render_to_response('reports/list.html', locals())


@login_required
def display(request, id):
    report = Report.objects.get(id=id)
    # perform advanced search and return contacts (make a function)
    contacts = makeadvfilter(report)
    # somehow get the attr names and variables to display in the template
    displayfields = [] # list of (field_name, verbose_name) for each field to be displayed
    displaydata = []   # list of (field_name, data) for each contact
    reportdata = []
    tmp = []
    for f in Report._meta.fields:
        if f.get_internal_type() == 'BooleanField' and f.value_from_object(report):
            displayfields.append((f.name, f.verbose_name))
            tmp.append(f.verbose_name)
    reportdata.append(tmp)
    for c in contacts:
        newcontact = []
        tmp = []
        for f in displayfields:
            newcontact.append((f[0], getattr(c, f[0])))
            tmp.append(getattr(c, f[0]))
        reportdata.append(tmp)
        displaydata.append(newcontact)
    request.session['reportname'] = report.name
    request.session['report'] = reportdata
    request.session['reportpagesize'] = (8.5, 11)   # Portrait size
    if report.page_size == "Landscape":
        request.session['reportpagesize'] = (11, 8.5)

    can_export = request.user.has_perm('reports.can_export')

    return render_to_response('reports/display.html', locals())


@login_required
def deletereport(request, id):
    report = Report.objects.get(id__exact=id)
    if request.method == "POST":
        if request.POST['submit'] == "Yes, delete the report":
            # delete the report and it's search.
            st = SearchTerms.objects.filter(report = report)
            for item in st:
                item.delete()
            report.delete()
            return HttpResponseRedirect('/reports/list/')
        elif request.POST['submit'] == "No, go back":
            return HttpResponseRedirect('/reports/list/')
        else:
            # This post is not from the confirm page.
            return HttpResponseRedirect('/reports/delete/%s/' % (report.id))
    else:
        # display the confirmation page
        return render_to_response('reports/delete_confirm.html', locals())


### helper functions
def makeadvfilter(r):
    """
    Retrieves the report's search terms and builds a Q filter. 

    arguments:
        *r* - The report for which to build a filter

    return:
        A Q filter of all the search terms, ready to apply to the base queryset.
    """

    contacts = Contact.objects.all()    # Brand new search results

    st = r.searchterms.all()
    filters = []
    ors = []
    for st in r.searchterms.all():
        attribute = st.field
        condition = st.condition
        query = st.query

        if st.operator == '':
            operator = 'and'
        else:
            operator = st.operator

        
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
                
                print("Is Empty")

            elif condition == "is not empty":
                attrstr = "%s__%s" % (attribute, "exact")
                query = ""
                q = ~Q( **{ str(attrstr) : str(query) } )
                
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

    return contacts
