from django import forms
from events.models import Event, Registrant
from contacts.models import Contact
import utils
from django.forms.util import ValidationError

class SavedSearchSelect(forms.Form):
    saved_search = utils.forms.DojoFilteredSelectField()

class EventForm(forms.ModelForm):
    start = forms.DateField(widget=forms.TextInput(attrs = dict(dojoType='dijit.form.DateTextBox',
                                                                required="true",
                                                                ),
                                                   )
                            )

    end = forms.DateField(widget=forms.TextInput(attrs = dict(dojoType='dijit.form.DateTextBox',
                                                                required="true",
                                                                ),
                                                   )
                            )

    title = forms.CharField(widget=forms.TextInput(attrs = dict(dojoType='dijit.form.TextBox',
                                                                required="true",
                                                                ),
                                                   )
                            )

    description = forms.CharField(widget=forms.Textarea(attrs = dict(dojoType='dijit.form.Textarea',
                                                                     required="true",
                                                                     style = "_height: 100px;min-height:100px;",

                                                                ),
                                                   )
                            )

    location = forms.CharField(widget=forms.TextInput(attrs = dict(dojoType='dijit.form.TextBox',
                                                                required="true",
                                                                ),
                                                   )
                            )

    allowed_attendies = forms.IntegerField(widget=forms.TextInput(attrs = dict(dojoType='dijit.form.ValidationTextBox',
                                                                               required="false",
                                                                               trim="true",
                                                                               regExp="[0-9]+",
                                                                               invalidMessage="Number is invalid",
                                                                               isValid='customIsValid',

                                                                ),
                                                   )
                            )

    payment_link = forms.URLField(widget=forms.TextInput(attrs = dict(dojoType='dijit.form.TextBox',
                                                                required="false",
                                                                ),
                                                   )
                            )


    web_confirmation_message = forms.CharField(label = "Web registration message", widget = utils.widgets.DojoDivWidget(), required=False)
    email_confirmation_message = forms.CharField(widget = utils.widgets.DojoDivWidget(), required=False)
    pending_message = forms.CharField(widget = utils.widgets.DojoDivWidget(), required=False)

    class Meta:
        model = Event
        exclude = ('registrants',)
        
class EventRegistrationForm(forms.Form):
    first_name = utils.forms.DojoTextField(required=True)
    last_name = utils.forms.DojoTextField()
    middle_initial = utils.forms.DojoTextField()
    title = utils.forms.DojoTextField()
    email = utils.forms.DojoTextField()
    phone1 = utils.forms.DojoTextField(label="Phone")
    addr1_row1 = utils.forms.DojoTextField(label="Address")
    addr1_row2 = utils.forms.DojoTextField(label="", required=False)
    addr1_city = utils.forms.DojoTextField(label="City")
    addr1_state = utils.forms.DojoTextField(label="State")
    addr1_zip = utils.forms.DojoZipCodeField(label="Zip Code")
    addr1_country = utils.forms.DojoTextField(label="Country")

    discount_code = utils.forms.DojoTextField(label="Discount Code", required=False)

    def clean_email(self):
        email = self.cleaned_data['email']

        # See if email exists
        contacts = Contact.objects.filter(email = email)
        if len(contacts) > 0:
            raise ValidationError, 'Email has already been registered'

    def save(self, event = None):
        assert event
        contact = Contact(first_name = self.cleaned_data['first_name'],
                          middle_initial = self.cleaned_data['middle_initial'],
                          last_name = self.cleaned_data['last_name'],
                          title = self.cleaned_data['title'],
                          email = self.cleaned_data['email'],
                          phone1 = self.cleaned_data['phone1'],
                          addr1_row1 = self.cleaned_data['addr1_row1'],
                          addr1_row2 = self.cleaned_data['addr1_row2'],
                          addr1_city = self.cleaned_data['addr1_city'],
                          addr1_state = self.cleaned_data['addr1_state'],
                          addr1_zip = self.cleaned_data['addr1_zip'],
                          addr1_country = self.cleaned_data['addr1_country'])

        contact.save()

        registrant = Registrant(event = event,
                                contact = contact,
                                pending = True,
                                discount_code = self.cleaned_data['discount_code'])

        registrant.save()

        return registrant
        
class EventReRegistrationForm(forms.Form):
    first_name = utils.forms.DojoTextField(required=True)
    last_name = utils.forms.DojoTextField()
    middle_initial = utils.forms.DojoTextField(required=False)
    title = utils.forms.DojoTextField()
    phone1 = utils.forms.DojoTextField(label="Phone")
    addr1_row1 = utils.forms.DojoTextField(label="Address")
    addr1_row2 = utils.forms.DojoTextField(label="", required=False)
    addr1_city = utils.forms.DojoTextField(label="City")
    addr1_state = utils.forms.DojoStateField(label="State")
    addr1_zip = utils.forms.DojoZipCodeField(label="Zip Code")
    addr1_country = utils.forms.DojoTextField(label="Country")

    discount_code = utils.forms.DojoTextField(label="Discount Code", required=False)

    def save(self, event = None, contact = None):
        assert event
        assert contact
        contact.first_name = self.cleaned_data['first_name']
        contact.middle_initial = self.cleaned_data['middle_initial']
        contact.last_name = self.cleaned_data['last_name']
        contact.title = self.cleaned_data['title']
        contact.phone1 = self.cleaned_data['phone1']
        contact.addr1_row1 = self.cleaned_data['addr1_row1']
        contact.addr1_row2 = self.cleaned_data['addr1_row2']
        contact.addr1_city = self.cleaned_data['addr1_city']
        contact.addr1_state = self.cleaned_data['addr1_state']
        contact.addr1_zip = self.cleaned_data['addr1_zip']
        addr1_country = self.cleaned_data['addr1_country']

        contact.save()

        registrant = Registrant(event = event,
                                contact = contact,
                                pending = True,
                                discount_code = self.cleaned_data['discount_code'])

        registrant.save()
        return registrant
