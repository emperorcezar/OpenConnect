from django.utils.translation import ugettext as _
from south.db import db
from contacts.models import *

class Migration:
    def forwards(self):
        db.execute('ALTER TABLE contacts_contact MODIFY COLUMN addr1_state VARCHAR(255) NULL')
        db.execute('ALTER TABLE contacts_contact MODIFY COLUMN addr2_state VARCHAR(255) NULL')

    def backwards(self):
        db.execute('ALTER TABLE contacts_contact MODIFY COLUMN addr1_state VARCHAR(2) NULL')
        db.execute('ALTER TABLE contacts_contact MODIFY COLUMN addr2_state VARCHAR(2) NULL')

        


