import re
from django import forms
from utils import widgets
from django.contrib.localflavor.us.us_states import STATE_CHOICES
from django.contrib.localflavor.us.forms import USStateField, USZipCodeField

'''
Specialized form fields. Many are just dojo equivalents that inherrit from
django defaults and set the widget

'''

class DojoTextField(forms.CharField):
    def __init__(self, *args, **kwargs):
        super(DojoTextField, self).__init__(*args, **kwargs)
        self.widget = widgets.DojoTextWidget(required = kwargs.get('required', False))

class DojoFilteredSelectField(forms.ChoiceField):
     def __init__(self, *args, **kwargs):
         super(DojoFilteredSelectField, self).__init__(*args, **kwargs)
         self.widget = widgets.DojoFilterSelectWidget(required = kwargs.get('required', False))

class DojoModelChoiceField(forms.ModelChoiceField):
    def __init__(self, *args, **kwargs):
        self.widget = widgets.DojoFilterSelectWidget(required = kwargs.get('required', False))
        super(DojoModelChoiceField, self).__init__(*args, **kwargs)

class DojoZipCodeField(USZipCodeField):
    def __init__(self, *args, **kwargs):
        super(DojoZipCodeField, self).__init__(*args, **kwargs)
        self.widget = widgets.DojoRegexTextWidget(required = kwargs.get('required', False), regExp='^\d{5}(?:-\d{4})?$')


class DojoStateField(USStateField):
    def __init__(self, *args, **kwargs):
        super(DojoStateField, self).__init__(*args, **kwargs)
        self.widget = widgets.DojoStateSelectWidget(required = kwargs.get('required', False))

class CurrencyField (forms.RegexField):
    currencyRe = re.compile(r'^[0-9]{1,5}(.[0-9][0-9])?$')
    def __init__(self, *args, **kwargs):
        super(CurrencyField, self).__init__(
            self.currencyRe, None, None, *args, **kwargs)

    def clean(self, value):
        value = super(CurrencyField, self).clean(value)
        return float(value)

class CurrencyInput (forms.TextInput):
    def render(self, name, value, attrs=None):
        if value != '':
            try:
                value = u"%.2f" % value
            except TypeError:
                pass
        return super(CurrencyInput, self).render(name, value, attrs)

