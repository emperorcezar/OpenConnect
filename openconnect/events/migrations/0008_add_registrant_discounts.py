from django.utils.translation import ugettext as _
from south.db import db
from events.models import *
from utils.slugs import AutoSlugField

class Migration:
    def forwards(self):
        db.add_column('events_registrant','discount_code', models.CharField(max_length = 40, blank=True))
        
    def backwards(self):
        db.delete_column('events_registrant','discount_code')
        
