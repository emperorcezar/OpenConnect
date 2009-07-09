from django.utils.translation import ugettext as _
from south.db import db
from events.models import *
from utils.slugs import AutoSlugField

class Migration:
    def forwards(self):
        db.add_column('events_event','pending_message', models.TextField(blank=True, null=True))

    def backwards(self):
        db.delete_column('events_event','pending_message')

        
