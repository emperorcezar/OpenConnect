
from south.db import db
from django.db import models
from events.models import *

class Migration:
    
    def forwards(self):
        
        # Model 'Event'
        db.create_table('events_event', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('title', models.CharField(max_length=255)),
            ('description', models.TextField()),
            ('start', models.DateField()),
            ('end', models.DateField()),
            ('location', models.CharField(max_length=255)),
            ('allowed_attendies', models.IntegerField(null=True, blank=True)),
            ('last_edited', models.DateField(auto_now = True)),
        ))
        # Mock Models
        Event = db.mock_model(model_name='Event', db_table='events_event', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField, pk_field_args=[])
        Contact = db.mock_model(model_name='Contact', db_table='contacts_contact', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField, pk_field_args=[])
        
        # M2M field 'Event.registrants'
        db.create_table('events_event_registrants', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('event', models.ForeignKey(Event, null=False)),
            ('contact', models.ForeignKey(Contact, null=False))
        )) 
        
        db.send_create_signal('events', ['Event'])
    
    def backwards(self):
        db.delete_table('events_event_registrants')
        db.delete_table('events_event')
        
