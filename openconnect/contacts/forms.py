import re
from django import forms
from django.forms.util import ValidationError
from contacts.models import Contact
from tagging.forms import TagField
from django.forms.fields import Select, ChoiceField, CharField
from utils.widgets import DojoComboBoxWidget
from django.contrib.localflavor.us.us_states import STATE_CHOICES

phone_re = re.compile(r'^\+*((\()|(\))|( )|(\.)|(-)|(\d+))+$')

# field for grouped choices, handles cleaning of funky choice tuple
class CustomChoiceField(ChoiceField):
        
    def clean(self, value):
        return value


class AddContact(forms.ModelForm):



    addr1_state = CharField(label = 'Primary State', required=False)
    addr2_state = CharField(label = 'Secondary State', required=False)


    def __init__(self, *args, **kwargs):
        choices = (('',''),) + STATE_CHOICES
        super(AddContact, self).__init__(*args, **kwargs)
    
            
        self.fields.insert(3, 'tag_list', CharField(required=False,
                                                    widget=forms.TextInput(attrs = dict(dojoType='dojox.form.MultiComboBox',
                                                                                     store="tagstore",
                                                                                     required="false",
                                                                                     style="width:99%;",
                                                                                         ),
                                                                           )
                                                    )
                           )
        

        if 'instance' in kwargs:
            self.fields['tag_list'].initial = kwargs['instance'].tag_list

        


    def save(self, *args, **kwargs):
        contact = super(AddContact, self).save(*args, **kwargs)
        try:
            kwargs['commit']
            if kwargs['commit'] != False:
                contact.tag_list = self.cleaned_data['tag_list']
        except KeyError:
            contact.tag_list = self.cleaned_data['tag_list']

        return contact
    
    class Meta:
        model = Contact
        exclude = ('token',)

    def clean_phone1(self):
        phone = self.cleaned_data['phone1']

        if phone in (None, ''):
            return phone

        if not phone_re.match(phone):
            raise ValidationError, "Number is not a valid number, must contain only periods, spaces, dashes, and numbers"
        else:
            return phone

    def clean_phone2(self):
        phone = self.cleaned_data['phone2']

        if phone in (None, ''):
            return phone

        if not phone_re.match(phone):
            raise ValidationError, "Number is not a valid number, must contain only periods, spaces, dashes, and numbers"
        else:
            return phone

    def clean_fax1(self):
        fax = self.cleaned_data['fax1']

        if fax in (None, ''):
            return fax

        if not phone_re.match(fax):
            raise ValidationError, "Number is not a valid number, must contain only periods, spaces, dashes, and numbers"
        else:
            return fax

    def clean_fax2(self):
        fax = self.cleaned_data['fax2']

        if fax in (None, ''):
            return fax

        if not phone_re.match(fax):
            raise ValidationError, "Number is not a valid number, must contain only periods, spaces, dashes, and numbers"
        else:
            return fax


    def clean_email(self):
        email = self.cleaned_data['email']

        if self.instance:
            if self.instance.email == email:
                return email

        if email == '':
            return email


        if self.instance.email == email:
            return email
        
        # See if email exists
        if email not in ('', None):
            try:
                Contact.objects.get(email = email)
            except Contact.DoesNotExist:
                return email
            else:
                raise ValidationError, 'Email exists. This contact is probably already registered.'
        else:
            return email

class SelfRegistration(forms.ModelForm):
    class Meta:
        model = Contact
        exclude = ('notes',)



class BasicSearch(forms.Form):
    first_name = forms.CharField(max_length=255, required=False)
    last_name = forms.CharField(max_length=255, required=False)
    email = forms.EmailField(required=False)
    tags = forms.CharField(max_length=255, required=False)

class ImportContactFile(forms.Form):
    file = forms.FileField()

