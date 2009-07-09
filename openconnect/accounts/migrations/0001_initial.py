
from south.db import db
from accounts.models import *

class Migration:
    
    def forwards(self):
        
        
        # Mock Models
        User = db.mock_model(model_name='User', db_table='auth_user', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        
        # Model 'UserProfile'
        db.create_table('accounts_userprofile', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('user', models.ForeignKey(User, unique=True)),
            ('pagingprefs', models.IntegerField()),
        ))
        
        db.send_create_signal('accounts', ['UserProfile'])
    
    def backwards(self):
        db.delete_table('accounts_userprofile')
        
