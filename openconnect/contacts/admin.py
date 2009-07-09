from django.contrib import admin
from contacts.models import *

admin.site.register(Contact)
admin.site.register(ContactEditHistory)
admin.site.register(ContactSavedSearch)

