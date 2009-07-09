
from south.db import db
from accounts.models import *

class Migration:
    
    def forwards(self):
        
        
        # Mock Models
        User = db.mock_model(model_name='User', db_table='auth_user', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        
        # Model 'EmailAlias'
        db.create_table('accounts_emailalias', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('email', models.EmailField()),
            ('user', models.ForeignKey(User, related_name="email_aliases")),
        ))
        
        db.send_create_signal('accounts', ['EmailAlias'])
    
    def backwards(self):
        db.delete_table('accounts_emailalias')
        
