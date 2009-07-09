
from south.db import db
from contacts.models import *

class Migration:
    
    def forwards(self):
        
        # Model 'Contact'
        db.create_table('contacts_contact', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('first_name', models.CharField(max_length=255)),
            ('middle_initial', models.CharField(max_length=1, blank=True, null=True)),
            ('last_name', models.CharField(max_length=255)),
            ('title', models.CharField(max_length=255, blank=True, null=True)),
            ('email', models.EmailField()),
            ('phone1', PhoneNumberField('Primary Phone Number', blank=True, null=True)),
            ('phone2', PhoneNumberField('Secondary Phone Number', blank=True, null=True)),
            ('fax1', PhoneNumberField('Primary Fax', blank=True, null=True)),
            ('fax2', PhoneNumberField('Secondary Fax', blank=True, null=True)),
            ('employer', models.CharField(max_length=255, blank=True, null=True)),
            ('position', models.CharField(max_length=255, blank=True, null=True)),
            ('addr1_row1', models.CharField('Row 1', max_length=255, blank=True, null=True)),
            ('addr1_row2', models.CharField('Row 2', max_length=255, blank=True, null=True)),
            ('addr1_city', models.CharField('City', max_length=255, blank=True, null=True)),
            ('addr1_state', USStateField('State', default='', blank=True, null=True)),
            ('addr1_zip', models.CharField('Zip Code', max_length=255, blank=True, null=True)),
            ('addr2_row1', models.CharField('Row 1', max_length=255, blank=True, null=True)),
            ('addr2_row2', models.CharField('Row 2', max_length=255, blank=True, null=True)),
            ('addr2_city', models.CharField('City', max_length=255, blank=True, null=True)),
            ('addr2_state', USStateField('State', blank=True, null=True)),
            ('addr2_zip', models.CharField('Zip Code', max_length=255, blank=True, null=True)),
            ('degree1', models.CharField('Degree', max_length=255, blank=True, null=True)),
            ('major1', models.CharField('Major', max_length=255, blank=True, null=True)),
            ('year1', models.IntegerField('Year', max_length=255, blank=True, null=True)),
            ('degree2', models.CharField('Degree', max_length=255, blank=True, null=True)),
            ('major2', models.CharField('Major', max_length=255, blank=True, null=True)),
            ('year2', models.IntegerField('Year', max_length=255, blank=True, null=True)),
            ('tag_list', models.CharField(max_length=255, blank=True)),
            ('do_not_email', models.BooleanField(blank=True, default=False)),
            ('preferred_comm', models.CharField(blank=True, default="email", max_length=255, choices=(('email', 'Email'), ('phone','Phone'), ('mail', 'Mail')))),
            ('notes', models.TextField(blank=True, null=True)),
        ))
        
        # Mock Models
        Contact = db.mock_model(model_name='Contact', db_table='contacts_contact', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        User = db.mock_model(model_name='User', db_table='auth_user', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        
        # Model 'ContactEditHistory'
        db.create_table('contacts_contactedithistory', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('contact', models.ForeignKey(Contact)),
            ('user', models.ForeignKey(User, blank=True, null=True)),
            ('event_date', models.DateTimeField(auto_now = True)),
            ('message', models.CharField(max_length=255)),
        ))
        
        # Mock Models
        User = db.mock_model(model_name='User', db_table='auth_user', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        
        # Model 'ContactSavedSearch'
        db.create_table('contacts_contactsavedsearch', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('user', models.ForeignKey(User)),
            ('name', models.CharField(max_length=255)),
            ('event_date', models.DateTimeField(auto_now = True)),
        ))
        # Mock Models
        ContactSavedSearch = db.mock_model(model_name='ContactSavedSearch', db_table='contacts_contactsavedsearch', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        Contact = db.mock_model(model_name='Contact', db_table='contacts_contact', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        
        # M2M field 'ContactSavedSearch.contact_list'
        db.create_table('contacts_contactsavedsearch_contact_list', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('contactsavedsearch', models.ForeignKey(ContactSavedSearch, null=False)),
            ('contact', models.ForeignKey(Contact, null=False))
        )) 
        
        db.send_create_signal('contacts', ['Contact','ContactEditHistory','ContactSavedSearch'])
    
    def backwards(self):
        db.delete_table('contacts_contactsavedsearch_contact_list')
        db.delete_table('contacts_contactsavedsearch')
        db.delete_table('contacts_contactedithistory')
        db.delete_table('contacts_contact')
        
