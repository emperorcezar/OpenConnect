from django.utils.translation import ugettext as _
from south.db import db
from contacts.models import *

class Migration:
    def forwards(self):
        db.execute('ALTER TABLE contacts_contact ADD UNIQUE(email)')
    def backwards(self):
        db.execute('ALTER TABLE contacts_contact DROP INDEX(email)')


