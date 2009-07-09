import smtplib, sys, os, re
from django.core.mail import EmailMultiAlternatives
from django.utils.encoding import force_unicode
import logging

env = os.environ
env['PYTHON_PATH'] = '/code/openconnect/openconnect/:/code/openconnect/'
env['DJANGO_SETTINGS_MODULE'] = 'settings'


# Setup Django Environment
sys.path.extend(os.environ['PYTHON_PATH'].split(':'))
from django.conf import settings

from django.contrib.sites.models import Site

current_site = Site.objects.get(id=settings.SITE_ID)
DOMAIN = current_site


from django.core.urlresolvers import reverse
from emails.models import Email
from contacts.models import Contact
from utils.html import pretty_print

logger = logging.getLogger("email_sender")
logger.setLevel(logging.INFO)
#create console handler and set level to debug
file_handler = logging.FileHandler(settings.LOG_FILE)
file_handler.setLevel(logging.INFO)
#create formatter
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
#add formatter to ch
file_handler.setFormatter(formatter)
#add ch to logger
logger.addHandler(file_handler)

from django.core.mail import SMTPConnection

class CustomSMTPConnection(SMTPConnection):
    """Simple override of SMTPConnection to allow a Return-Path to be specified"""
    def __init__(self, return_path=None, **kwargs):
        self.return_path = return_path
        super(CustomSMTPConnection, self).__init__(**kwargs)
    
    def _send(self, email_message):
        """A helper method that does the actual sending."""
        if not email_message.to:
            return False
        try:
            return_path = self.return_path or email_message.from_email
            self.connection.sendmail(return_path,
                    email_message.recipients(),
                    email_message.message().as_string())
        except:
            if not self.fail_silently:
                raise
            return False
        return True


def get_from(email):
    if email.from_email:
        return "%s <%s>" % (email.from_email.name, email.from_email.email)
    else:
        assert email.user.email
        return "%s %s <%s>" % (email.user.first_name, email.user.last_name, email.user.email)


e_id = sys.argv[-1]
e = Email.objects.get(id=e_id)

connection = CustomSMTPConnection(return_path = e.user.email)

for c in e.recipients.all()[253:]:
    print "Sending to %s" % (c,)
    if c.do_not_email:
        continue

    if not c.email or c.email == '':
        continue
    
    message = e.message + u"<br><br><span style='font-size: 10px;'>You received this email because of your previous relationship with the IIT Institute of Design.  To unsubscribe, <a href='http://%s/emails/unsubscribe/[id]/'>click here</a>." % settings.DOMAIN
    message = re.sub(u'\[first[_ ]name\]',c.first_name,message)
    message = re.sub(u'\[last[_ ]name\]',c.last_name,message)
    message = re.sub(u'\[id\]',"%d" % c.id,message)
           
    html_message = force_unicode(pretty_print(message))

    if e.event:
        message = re.sub(u'\[register[_ ]link\]',u'http://'+settings.DOMAIN+reverse('event-register-token', kwargs={'slug':e.event.slug, 'token':c.get_token()}),message)

    if e.event:
        html_message = re.sub(u'\[register[_ ]link\]',u'<a href="http://'+settings.DOMAIN+reverse('event-register', kwargs={'slug':e.event.slug})+'">register</a>',html_message)
    
    mail = EmailMultiAlternatives(e.subject, force_unicode(pretty_print(message)), get_from(e), ['"%s %s" <%s>' % (c.first_name, c.last_name, c.email)], connection = connection)
    #mail = EmailMultiAlternatives(e.subject, pretty_print(message), from_email, ['cezar@id.iit.edu'])

    mail.attach_alternative(force_unicode(message), "text/html")

    if e.attachment:
        print "attached"
        mail.attach_file(e.attachment.path)

    mail.send()
    print "email sent"
    logger.info("Sent Email To:%s - From:%s - Subject:%s" % (c.email, get_from(e), e.subject))

