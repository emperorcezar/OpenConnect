from django.utils.translation import ugettext as _
from south.db import db
from reports.models import *


class Migration:
    def forwards(self):
        db.add_column('reports_report','addr1_country', models.BooleanField("Country"))
        db.add_column('reports_report','addr2_country', models.BooleanField("Country"))

    def backwards(self):
        db.delete_column('reports_report','addr1_country')
        db.delete_column('reports_report','addr2_country')

