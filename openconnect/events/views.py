import sha
import random
import datetime
import time
from utils.render import render_to_response
from utils.html import pretty_print
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.generic.list_detail import object_list
from events.models import Event, Registrant, Pricing
from emails.models import Email
from events.forms import EventForm, EventRegistrationForm, EventReRegistrationForm, SavedSearchSelect
from contacts.models import Contact, ContactSavedSearch
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404 as get
from django.utils import simplejson
import django.dispatch
from utils import email_log
from django.conf import settings
from django.template.loader import render_to_string
from django.contrib.sites.models import Site

FROM_EMAIL = settings.FROM_EMAIL

current_site = Site.objects.get(id=settings.SITE_ID)


DOMAIN = current_site.domain

# Create pending complete signal
pending_complete_signal = django.dispatch.Signal()
pending_signal = django.dispatch.Signal()

DEFAULT_DATE_INPUT_FORMATS = (
    '%Y-%m-%d', '%m/%d/%Y', '%m/%d/%y', # '2006-10-25', '10/25/2006', '10/25/06'
    '%b %d %Y', '%b %d, %Y',            # 'Oct 25 2006', 'Oct 25, 2006'
    '%d %b %Y', '%d %b, %Y',            # '25 Oct 2006', '25 Oct, 2006'
    '%B %d %Y', '%B %d, %Y',            # 'October 25 2006', 'October 25, 2006'
    '%d %B %Y', '%d %B, %Y',            # '25 October 2006', '25 October, 2006'
)

EMPTY_VALUES = (None, '')

def get_date(value):
    """
    Validates that the input can be converted to a date. Returns a Python
    datetime.date object.
    """

    if value in EMPTY_VALUES:
        return None
    if isinstance(value, datetime.datetime):
        return value.date()
    if isinstance(value, datetime.date):
        return value
    for format in DEFAULT_DATE_INPUT_FORMATS:
        try:
            return datetime.date(*time.strptime(value, format)[:3])
        except ValueError:
            continue
    raise ValidationError(u'Enter a valid date.')


@login_required
def pricing_add(request):
    event = get(Event, id=request.POST.get('event', None))
    price = request.POST.get('price', None)
    discount_code = request.POST.get('discount_code', '')
    tag_list = request.POST.get('tag_list', '')
    start = get_date(request.POST.get('start', None))
    end = get_date(request.POST.get('end', None))

    assert price

    p = Pricing(event=event, price=price, discount_code=discount_code, tag_list=tag_list, start=start, end=end)
    p.save()

    start_string = ''
    end_string = ''

    if p.start:
        start_string = p.start.strftime('%m/%d/%Y')

    if p.end:
        end_string = p.end.strftime('%m/%d/%Y')
        
    response = {'status':'success',
                'price':price,
                'discount_code':discount_code,
                'tag_list':tag_list,
                'id':p.id,
                'start': start_string,
                'end': end_string,
                }
    return HttpResponse("%s" % simplejson.dumps(response))

@login_required
def pricing_delete(request):
    p = get(Pricing, id=request.GET.get('id', None))
    p.delete()

    response = {'status':'success',}
    return HttpResponse("%s" % simplejson.dumps(response))
    

    
@login_required
def listing(request):
    raise NotImplimentedError

@login_required
def emails(request, id):
    event = get(Event, pk=id)
    emails = Email.objects.filter(event = event)
    return render_to_response('event_emails.html', locals())

@login_required
def invite(request, id):
    event = get(Event, pk=id)
    email = Email(user = request.user,
                  subject = "You're invited to %s" % (event.title),
                  message = render_to_string("event_invite_email.txt", locals()),
                  event = event
                  )
    email.save()
    return HttpResponseRedirect(reverse('emails-update', args=[email.id]))

@login_required
def delete(request, id):
    event = get(Event, pk=id)
    event.delete()
    return HttpResponseRedirect(reverse('events'))

@login_required
def add(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save()
            return HttpResponseRedirect(reverse('event-edit', args=[event.id])+'?after_add=1')
    else:
        form = EventForm()

    return render_to_response('event_add.html', locals())

@login_required
def edit(request, id):
    instance = get(Event, pk=id)

    after_add = request.GET.get('after_add', None)

    pricing = instance.pricing_set.all()
    
    if request.method == 'POST':
        form = EventForm(request.POST, instance = instance)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('events'))
    else:
        form = EventForm(instance = instance)

    return render_to_response('event_edit.html', locals())

@login_required
def event_show(request, slug):
    object = get(Event, slug=slug)
    return render_to_response('event_details.html', locals())

@login_required
def pending_toggle(request):
    event_id = request.POST.get('event', None)
    contact_id = request.POST.get('contact', None)
    contact = get(Contact, pk=contact_id)
    event = get(Event, pk=event_id)

    instance = get(Registrant, contact=contact, event=event)

    if instance.pending == 1:
        instance.pending = False
        instance.save()
        # send signal
        pending_complete_signal.send(sender=instance, contact=contact, event=event)
    else:
        instance.pending = True
        instance.save()

    return HttpResponse(contact_id)

@login_required
def registrants_pending_status(request, id):
    event = get(Event, pk=id)
    registrants = event.registrant_set.all()

    return render_to_response('registrants_pending_status.html', locals())

def pending_complete_email(sender, contact=None, event=None, **kwargs):
    assert event
    assert contact
    from django.core.mail import EmailMultiAlternatives

    price = event.get_price(contact)


    if event.email_confirmation_message:
        custom_text = pretty_print(event.email_confirmation_message)

        mail = EmailMultiAlternatives("Registration complete for %s" %(event, ),
                                  render_to_string("registration_complete.txt", locals()),
                                  FROM_EMAIL,
                                  ['"%s %s" <%s>' % (contact.first_name, contact.last_name, contact.email)]
                                  )

        mail.attach_alternative(render_to_string("registration_complete.html", locals()), "text/html")
        mail.send()
        email_log.info("Sent Email To:%s - From:%s - Subject:%s" % (contact.email, FROM_EMAIL, "Instructions to complete registration for %s" %(event, )))

pending_complete_signal.connect(pending_complete_email)

def pending_email(sender, contact=None, event=None, **kwargs):
    assert event
    assert contact
    from django.core.mail import EmailMultiAlternatives

    price = event.get_price(contact)

    if event.pending_message:
        custom_text = pretty_print(event.pending_message)

        mail = EmailMultiAlternatives("Registration pending for %s" %(event, ),
                                      render_to_string("registration_pending.txt", locals()),
                                      FROM_EMAIL,
                                      ['"%s %s" <%s>' % (contact.first_name, contact.last_name, contact.email)]
                                      )

        mail.attach_alternative(render_to_string("registration_pending_email.html", locals()), "text/html")
        mail.send()
        email_log.info("Sent Email To:%s - From:%s - Subject:%s" % (contact.email, FROM_EMAIL, "Registration pending for %s" %(event, )))

pending_signal.connect(pending_email)

def email_register(request, slug):
    if request.method == 'POST':
        contact = get(Contact, email=request.POST.get('email', None))
        event = get(Event, slug=slug)
        registrant = Registrant(contact = contact, event = event, pending = True, discount_code = request.POST.get('discount_code', None))
        try:
            registrant.save()
        except ValueError, e:
            if str(e) == 'Already Registered':
                error = 'That email address is already registered'
                return render_to_response('event_email_register.html', locals())
            else:
                print e
                raise

        from django.core.mail import EmailMultiAlternatives


            

        incorrect_link = "http://"+DOMAIN+reverse('event-register-token', kwargs={'slug':slug,'token':contact.get_token()})+"/"

        message = render_to_string("email_register_message.txt", locals())
        html_message = render_to_string("email_register_message.html", locals())
        
        mail = EmailMultiAlternatives("Registration Confirmation for %s" %(event, ),
                                      message,
                                      FROM_EMAIL,
                                      ['"%s %s" <%s>' % (contact.first_name, contact.last_name, contact.email)]
                                      )

        mail.attach_alternative(html_message, "text/html")
        mail.send()
        email_log.info("Sent Email To:%s - From:%s - Subject:%s" % (contact.email, FROM_EMAIL, "Registration Confirmation For %s" %(event, )))
        
        
        return render_to_response('registration_pending.html', locals())
    
    return render_to_response('event_email_register.html', locals())

def register(request, slug):
    event = get(Event, slug=slug)
    if request.method == 'POST':
        form = EventRegistrationForm(request.POST)

        if form.is_valid():
            registrant = form.save(event = event)
            pending_signal.send(sender=registrant, contact=registrant.contact, event=event)

            return render_to_response('registration_pending.html', locals())
        else:
            return render_to_response('event_register.html', locals())

    else:
        form = EventRegistrationForm()
        return render_to_response('event_register.html', locals())

def token_register(request, slug, token):
    event = get(Event, slug=slug)
    print "Token: " + token
    contact = get(Contact, token=token)

    if request.method == 'POST':
        form = EventReRegistrationForm(request.POST)

        if form.is_valid():
            registrant = form.save(event = event, contact = contact)
            pending_signal.send(sender=registrant, contact=registrant.contact, event=event)

            return render_to_response('registration_pending.html', locals())
        else:
            return render_to_response('event_register.html', locals())

    else:
        data = {'first_name':contact.first_name,
                'middle_initial':contact.middle_initial,
                'last_name':contact.last_name,
                'title':contact.title,
                'email':contact.email,
                'phone1':contact.phone1,
                'addr1_row1':contact.addr1_row1,
                'addr1_row2':contact.addr1_row2,
                'addr1_city':contact.addr1_city,
                'addr1_state':contact.addr1_state,
                'addr1_zip':contact.addr1_zip,
                'addr1_country':contact.addr1_country,
                }
        form = EventReRegistrationForm(data)
        
        return render_to_response('event_register.html', locals())

def search(request):
    if request.method == 'GET':
        return render_to_response('event_search.html', locals())

def execute_search(request):

    search = request.POST.get('search', None)
    date = request.POST.get('date', None)

    response = {}
    response['results'] = []

    if search:
        title_results = Event.objects.filter(title__icontains = search)
        description_results = Event.objects.filter(description__icontains = search)

        results = title_results | description_results

    if date:
        date_results = Event.objects.filter(start__lte=date, end__gte=date)

    if not search and date:
        results = date_results
    
    for event in results:
        response['results'].append({'id':event.id, 'title':event.title, 'link':reverse('event-show', args=[event.slug]), 'start':str(event.start), 'end': str(event.end), 'description':event.short_description()})

    response['num_results'] = len(results)

    time.sleep(1)
        
    return HttpResponse("%s" % simplejson.dumps(response))
