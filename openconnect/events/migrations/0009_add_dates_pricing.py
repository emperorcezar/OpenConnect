from django.utils.translation import ugettext as _
from south.db import db
from events.models import *
from utils.slugs import AutoSlugField

class Migration:
    def forwards(self):
        db.add_column('events_pricing','start', models.DateField(blank=True, null=True))
        db.add_column('events_pricing','end', models.DateField(blank=True, null=True))

    def backwards(self):
        db.delete_column('events_pricing','start')
        db.delete_column('events_pricing','end')
        
