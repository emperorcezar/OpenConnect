from django import forms
from reports.models import Report, SearchTerms

class CreateReport(forms.ModelForm):
    class Meta:
        model = Report
