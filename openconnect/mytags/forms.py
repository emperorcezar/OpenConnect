from django import forms
from tagging.models import Tag

class RenameTag(forms.ModelForm):
    class Meta:
        model = Tag

