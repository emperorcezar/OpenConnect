from django.utils.translation import ugettext as _
from south.db import db
from contacts.models import *

class Migration:
    def forwards(self):
        Event = db.mock_model(model_name='Event', db_table='events_event', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField, pk_field_args=[])
        db.add_column('emails_email','event', models.ForeignKey(Event, blank=True, null=True))
    
    def backwards(self):
        db.delete_column('emails_email','event_id')
