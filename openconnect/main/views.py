from django.template import RequestContext
from utils.render import render_to_response
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from contacts.models import Contact, ContactSavedSearch, ContactEditHistory
from contacts.forms import BasicSearch
from emails.models import Email
import csv
from utils.unicodecsv import UnicodeWriter

from django.utils import simplejson
from reportlab.platypus import SimpleDocTemplate, Spacer, Table, TableStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from django.template.defaultfilters import slugify
from tagging.models import Tag


@login_required
def json_tag_list(request):
    query = request.GET.get('q', '').replace('*', '')
    tags = Tag.objects.filter(name__startswith = query)

    json = {'identifier':'id', 'items':[]}
    
    for tag in tags:
        json['items'].append({'id':tag.id, 'name':str(tag.name)})

    return HttpResponse(simplejson.dumps(json), mimetype='text/json-comment-filtered')



@login_required
def index(request):
    form = BasicSearch()
    recentsearches = ContactSavedSearch.objects.filter(user=request.user).order_by("-event_date")[:3]
    recentdrafts = Email.objects.filter(user=request.user, status="draft").order_by("-last_edited")[:3]
    recentupdates = ContactEditHistory.objects.all().order_by("-event_date")[:3]
    recentunsubs = ContactEditHistory.objects.filter(message = "The contact has unsubscribed.").order_by("-event_date")[:3]
    return render_to_response('home.html', locals())

@login_required
def exportcsv(request, setname):
    if setname in ['newcontactscsv', 'existingcontactscsv', 'badcontactscsv', 'report']:
        # Create the HttpResponse object with the appropriate CSV header.
        response = HttpResponse(mimetype='text/csv')
        if setname == 'report':
            try:
                name = request.session['reportname']
            except KeyError:
                name = 'report'
                
            response['Content-Disposition'] = 'attachment; filename=' + name.replace(' ', '_') + '.csv'
        else:
            try:
                name = request.session['reportname']
            except KeyError:
                name = 'report'

            response['Content-Disposition'] = 'attachment; filename=' + name.replace(' ', '_') + '.csv'

        writer = UnicodeWriter(response)

        if setname in ['newcontactscsv', 'existingcontactscsv', 'badcontactscsv']:
            data = request.session[setname]
            names = []
            for cdict in data:
                if names == []:
                    names = cdict.keys()
                    writer.writerow(names)
                # print the row
                writer.writerow(cdict.values())
        else:
            data = request.session[setname]
            for row in data:
                writer.writerow(row)
    else:
        # Create the HttpResponse object with the appropriate CSV header.
        response = HttpResponse(mimetype='text/csv')
        response['Content-Disposition'] = 'attachment; filename=error.csv'
        writer = UnicodeWriter(response)
        writer.writerow(['error']) 
        writer.writerow(["'%s' is not a valid data set" % setname]) 

    return response

@login_required
def exportpdf(request, setname):
    (PAGEW, PAGEH) = request.session['reportpagesize']
    data = request.session[setname]
    try:
        name = request.session['reportname']
    except KeyError:
        name = 'report'
    response = HttpResponse(mimetype='application/pdf')
    response['Content-Disposition'] = 'attachment; filename='+slugify(name)+'.pdf'
    GRID_STYLE = TableStyle(
                    [('GRID', (0,0), (-1,-1), 0.25, colors.black),
                     ('ALIGN',(0,0),(-1,0),'CENTER'),]
                    )
    doc = SimpleDocTemplate( response, pagesize = (PAGEW*inch, PAGEH*inch), leftMargin = 0.5*inch, rightMargin = 0.5*inch, topMargin = 0.5*inch, bottomMargin = 0.5*inch )
    Story = [ ]
    # Add the table
    t = Table( data )
    t.setStyle( GRID_STYLE )
    for s in t.split((PAGEW-1)*inch, (PAGEH-1.15)*inch):
        Story.append( s )
        Story.append( Spacer( 1, 0.15*inch ) )
    doc.build( Story )
    return response
