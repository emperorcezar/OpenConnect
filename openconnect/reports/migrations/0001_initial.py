
from south.db import db
from reports.models import *

class Migration:
    
    def forwards(self):
        
        # Model 'Report'
        db.create_table('reports_report', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('name', models.CharField("Name of this report", max_length=255)),
            ('page_size', models.CharField(default="Portrait", choices=(("Portrait", "Portrait"),("Landscape","Landscape")), max_length=8)),
            ('first_name', models.BooleanField("First Name")),
            ('middle_initial', models.BooleanField("Middle Initial")),
            ('last_name', models.BooleanField("Last Name")),
            ('title', models.BooleanField("Title")),
            ('email', models.BooleanField("Email")),
            ('phone1', models.BooleanField("Primary Phone Number")),
            ('phone2', models.BooleanField("Secondary Phone Number")),
            ('fax1', models.BooleanField("Primary Fax")),
            ('fax2', models.BooleanField("Secondary Fax")),
            ('employer', models.BooleanField("Employer")),
            ('position', models.BooleanField("Position")),
            ('addr1_row1', models.BooleanField("Row 1")),
            ('addr1_row2', models.BooleanField("Row 2")),
            ('addr1_city', models.BooleanField("City")),
            ('addr1_state', models.BooleanField("State")),
            ('addr1_zip', models.BooleanField("Zip Code")),
            ('addr2_row1', models.BooleanField("Row 1")),
            ('addr2_row2', models.BooleanField("Row 2")),
            ('addr2_city', models.BooleanField("City")),
            ('addr2_state', models.BooleanField("State")),
            ('addr2_zip', models.BooleanField("Zip Code")),
            ('degree1', models.BooleanField("Degree")),
            ('major1', models.BooleanField("Major")),
            ('year1', models.BooleanField("Year")),
            ('degree2', models.BooleanField("Degree")),
            ('major2', models.BooleanField("Major")),
            ('year2', models.BooleanField("Year")),
            ('tag_list', models.BooleanField("Tags")),
            ('do_not_email', models.BooleanField("Do Not Email")),
            ('preferred_comm', models.BooleanField("Preferred Comm")),
            ('notes', models.BooleanField("Notes")),
        ))
        
        # Mock Models
        Report = db.mock_model(model_name='Report', db_table='reports_report', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        
        # Model 'SearchTerms'
        db.create_table('reports_searchterms', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('field', models.CharField(max_length=255)),
            ('condition', models.CharField(max_length=255)),
            ('query', models.CharField(max_length=255)),
            ('operator', models.CharField(max_length=255, blank=True)),
            ('order', models.IntegerField()),
            ('report', models.ForeignKey(Report, related_name="searchterms")),
        ))
        db.create_index('reports_searchterms', ['report_id','order'], unique=True, db_tablespace='')
        
        
        db.send_create_signal('reports', ['Report','SearchTerms'])
    
    def backwards(self):
        db.delete_table('reports_searchterms')
        db.delete_table('reports_report')
        
