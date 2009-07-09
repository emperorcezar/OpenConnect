from django.utils.translation import ugettext as _
from south.db import db
from events.models import *
from utils.slugs import AutoSlugField

class Migration:
    def forwards(self):
        db.alter_column('events_pricing', 'price', models.DecimalField(max_digits=12, decimal_places=2))

    def backwards(self):
        db.alter_column('events_pricing','price', models.FloatField())
        
