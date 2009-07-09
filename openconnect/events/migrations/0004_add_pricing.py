
from south.db import db
from django.db import models
from events.models import *

class Migration:
    
    def forwards(self):
        
        
        # Mock Models
        Event = db.mock_model(model_name='Event', db_table='events_event', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField, pk_field_args=[], pk_field_kwargs={})
        
        # Model 'Pricing'
        db.create_table('events_pricing', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('event', models.ForeignKey(Event)),
            ('price', models.FloatField()),
        ))
        
        db.send_create_signal('events', ['Pricing'])
    
    def backwards(self):
        db.delete_table('events_pricing')
        
