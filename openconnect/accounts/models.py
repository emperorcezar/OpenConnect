from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    pagingprefs = models.IntegerField()

# Putting this here because it's somewhat of a preference
class EmailAlias(models.Model):
    email = models.EmailField()
    name = models.CharField(max_length=255, null=True, blank=True)
    user = models.ForeignKey(User, related_name="email_aliases")

    def __unicode__(self):
        return self.email
