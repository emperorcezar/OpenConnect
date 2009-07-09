
from south.db import db
from emails.models import *

class Migration:
    
    def forwards(self):
        
        
        # Mock Models
        User = db.mock_model(model_name='User', db_table='auth_user', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        
        # Model 'Email'
        db.create_table('emails_email', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('subject', models.CharField(max_length=255)),
            ('attachment', models.FileField(upload_to="attachments/%Y/%m/%d", blank=True)),
            ('message', models.TextField(blank=True)),
            ('status', models.CharField(choices=(('draft', 'draft'),('template','template'),('sent','sent mail')), max_length=9)),
            ('user', models.ForeignKey(User, related_name="whocaresthiswillneverbereferenced")),
            ('last_edited', models.DateField(auto_now = True)),
        ))
        # Mock Models
        Email = db.mock_model(model_name='Email', db_table='emails_email', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        Contact = db.mock_model(model_name='Contact', db_table='contacts_contact', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        
        # M2M field 'Email.recipients'
        db.create_table('emails_email_recipients', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('email', models.ForeignKey(Email, null=False)),
            ('contact', models.ForeignKey(Contact, null=False))
        )) 
        
        db.send_create_signal('emails', ['Email'])
    
    def backwards(self):
        db.delete_table('emails_email_recipients')
        db.delete_table('emails_email')
        
