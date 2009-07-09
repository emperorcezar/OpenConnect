from django import forms
from emails.models import Email
from contacts.models import ContactSavedSearch
from accounts.models import EmailAlias
from events.models import Event
import utils

class CreateEmail(forms.ModelForm):
    #recipients = forms.CharField(widget=forms.Textarea(attrs={'rows': '3'}))
    message = forms.fields.CharField(widget=forms.widgets.Textarea(attrs={"dojoType":"dijit.Editor", "plugins":"['undo', 'redo', '|', 'bold', 'italic', 'underline', 'strikethrough', 'subscript', 'superscript', '|', 'insertOrderedList', 'insertUnorderedList', '|', 'indent', 'outdent', 'justifyCenter', 'justifyFull', 'justifyLeft', 'justifyRight']"}), required=False)
    event = utils.forms.DojoModelChoiceField(queryset=Event.objects.all(), required=False)

    def __init__(self, *args, **kwargs):
        try:
            user = kwargs.pop('user')
            email = user.email
        except KeyError:
            user = None
            email = "DEFAULT"

        super(CreateEmail, self).__init__(*args, **kwargs)
        print("user is %s" %(user,))
        self.fields['from_email'] = forms.ModelChoiceField(queryset=EmailAlias.objects.filter(user=user), empty_label=email, required=False)
    
    class Meta:
        model = Email
        exclude = ('status', 'user', 'recipients')

    def save(self, commit=True, extra_attrs={}):
        if self.cleaned_data['from_email'] == u'':
            self.cleaned_data['from_email'] = None

        # if no attachment, then don't change the current attachment.

        if self.cleaned_data['attachment'] in (None, ''):
            print "del"
            del self.cleaned_data['attachment']

        instance = super(CreateEmail, self).save(commit=False)
        # check if the message contains an &nbsp; and strip it
        instance.message.replace(u"\xa0", "")

        # strip strange character coming up
        instance.message = instance.message.replace(u'\xc3\x82', '')

        for key in extra_attrs.keys():
            setattr(instance, key, extra_attrs[key])
        instance.save()
        print "Attachment: %s" % (instance.attachment, )
        searchid = self.data.get('searchrecipients', "-9999")
        if searchid != "-9999":
            for c in instance.recipients.all():
                instance.recipients.remove(c)
            recips = ContactSavedSearch.objects.get(pk=searchid).contact_list.all()
            for c in recips:
                instance.recipients.add(c)
        instance.save()
        return instance
