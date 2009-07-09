from django.db import models
from django.contrib.auth.models import User
from contacts.models import Contact
from accounts.models import EmailAlias
from django.template.defaultfilters import wordcount


class Email(models.Model):
    recipients = models.ManyToManyField(Contact, blank=True, null=True, related_name="received_mail")
    subject = models.CharField(max_length=255)
    attachment = models.FileField(upload_to="attachments/%Y/%m/%d/%H_%M", blank=True)
    message = models.TextField(blank=True)
    status = models.CharField(choices=(('draft', 'draft'),('template','template'),('sent','sent mail')), max_length=9)
    user = models.ForeignKey(User, related_name="users")  # draft: the email owner.  template: NA.  sent: the sender.
    last_edited = models.DateField(auto_now = True)
    from_email = models.ForeignKey(EmailAlias, related_name="from_emails", null = True, blank = True)
    event = models.ForeignKey('events.Event', blank=True, null=True)

    def message_wordcount(self):
        return wordcount(self.message)

    def short_recipients(self):
        if len(self.recipients.all()) > 5:
            return self.recipients.all()[:4]
        else:
            return self.recipients.all()

    def __unicode__(self):
        return self.subject

    def __str__(self):
        return self.__unicode__()
