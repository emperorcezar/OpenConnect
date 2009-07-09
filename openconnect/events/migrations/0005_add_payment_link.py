from django.utils.translation import ugettext as _
from south.db import db
from events.models import *

class Migration:
    def forwards(self):
        db.add_column('events_event','payment_link', models.URLField(verify_exists=False))
    
    def backwards(self):
        db.delete_column('events_event','payment_link')
