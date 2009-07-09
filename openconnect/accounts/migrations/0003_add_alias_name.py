
from south.db import db
from accounts.models import *

class Migration:
    
    def forwards(self):
        db.add_column('accounts_emailalias','name', models.CharField(max_length=255, blank=True, null=True))
    
    def backwards(self):
        db.delete_column('accounts_emailalias', 'name')
        
