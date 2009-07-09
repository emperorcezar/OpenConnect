from django.utils.translation import ugettext as _
from south.db import db
from events.models import *

class Migration:
    def forwards(self):
        db.add_column('contacts_contact','addr1_country', models.CharField(max_length=255, blank=True, null=True))
        db.add_column('contacts_contact','addr2_country', models.CharField(max_length=255, blank=True, null=True))
        db.add_column('contacts_contact','school1', models.CharField(max_length=255, blank=True, null=True))
        db.add_column('contacts_contact','school2', models.CharField(max_length=255, blank=True, null=True))

    def backwards(self):
        db.delete_column('contacts_contact','addr1_country')
        db.delete_column('contacts_contact','addr2_country')
        db.delete_column('contacts_contact','school1')
        db.delete_column('contacts_contact','school2')
