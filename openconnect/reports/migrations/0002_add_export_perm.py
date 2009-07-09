from south.db import db
from django.contrib.auth.models import User, Permission, Group
from django.contrib.contenttypes.models import ContentType

class Migration:
    
    def forwards(self):
        content_type = ContentType.objects.get(app_label = 'reports', model = 'report')
        permission = Permission.objects.get_or_create(name = 'Can Export Reports', codename = 'can_export', content_type = content_type)

    def backwards(self):
        content_type = ContentType.objects.get(app_label = 'reports', model = 'report')
        permission = Permission.objects.get(name = 'Can Export Reports', codename = 'can_export', content_type = content_type)
        permission.delete()


