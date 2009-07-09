from django import template
from contacts.models import contactattrs

register = template.Library()

@register.inclusion_tag('adv_search_box.html')
def adv_search_box():
    return {'contactattrs':contactattrs}

