from django.utils.translation import ugettext as _
from south.db import db
from events.models import *
from utils.slugs import AutoSlugField

class Migration:
    def forwards(self):
        db.alter_column('events_event','title', models.CharField(max_length=255, unique=True))
        db.add_column('events_event','slug', AutoSlugField(max_length=255, populate_from='title'))
    def backwards(self):
        db.alter_column('events_event','title', models.CharField(max_length=255))
        db.delete_column('events_event','slug')
