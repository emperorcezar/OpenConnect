from django.utils.translation import ugettext as _
from south.db import db
from events.models import *

class Migration:
    def forwards(self):
        db.delete_column('contacts_contact','tag_list')
    
    def backwards(self):
        db.add_column('contacts_contact','tag_list', models.CharField(max_length=255, blank=True))
