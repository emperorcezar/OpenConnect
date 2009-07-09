from django.utils.translation import ugettext as _
from south.db import db
from contacts.models import *

class Migration:
    def forwards(self):
        db.execute('ALTER TABLE contacts_contact DROP INDEX email')
        db.execute('ALTER TABLE contacts_contact MODIFY COLUMN email VARCHAR(75) NULL')

    def backwards(self):
        db.execute('ALTER TABLE contacts_contact MODIFY COLUMN email VARCHAR(75) NOT NULL')
        db.execute('ALTER TABLE contacts_contact ADD UNIQUE(email)')
        


