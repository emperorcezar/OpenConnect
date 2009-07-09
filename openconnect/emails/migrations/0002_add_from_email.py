
from south.db import db
from emails.models import *

class Migration:
    
    def forwards(self):
        # Mock Models
        EmailAlias = db.mock_model(model_name='EmailAlias', db_table='accounts_emailalias', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        
        # Model 'Email'
        db.add_column('emails_email', 'from_email', models.ForeignKey(EmailAlias, null = True, blank = True))
    
    def backwards(self):
        db.delete_column('emails_email', 'from_email')
        
