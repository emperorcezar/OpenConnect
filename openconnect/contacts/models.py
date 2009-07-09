import sha
import random
from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
import tagging
from tagging.models import Tag
from django.contrib.localflavor.us.models import PhoneNumberField, USStateField
#from events.models import Event
# Create your models here.

class Contact(models.Model):
    first_name =        models.CharField(max_length=255)
    middle_initial =    models.CharField(max_length=1, blank=True, null=True)
    last_name =         models.CharField(max_length=255)
    title =             models.CharField(max_length=255, blank=True, null=True)
    email =             models.EmailField(null=True, blank=True)
    phone1 =            models.CharField('Primary Phone Number', blank=True, null=True, max_length=255)
    phone2 =            models.CharField('Secondary Phone Number', blank=True, null=True, max_length=255)
    fax1 =              models.CharField('Primary Fax', blank=True, null=True, max_length=255)
    fax2 =              models.CharField('Secondary Fax', blank=True, null=True, max_length=255)
    employer =          models.CharField(max_length=255, blank=True, null=True)
    position =          models.CharField(max_length=255, blank=True, null=True)
    addr1_row1 =        models.CharField('Row 1', max_length=255, blank=True, null=True)
    addr1_row2 =        models.CharField('Row 2', max_length=255, blank=True, null=True)
    addr1_city =        models.CharField('City', max_length=255, blank=True, null=True)
    addr1_state =       models.CharField('State', max_length=255, default='', blank=True, null=True)
    addr1_zip =         models.CharField('Zip Code', max_length=255, blank=True, null=True)
    addr1_country =     models.CharField('Country', max_length=255, blank=True, null=True)

    addr2_row1 =        models.CharField('Row 1', max_length=255, blank=True, null=True)
    addr2_row2 =        models.CharField('Row 2', max_length=255, blank=True, null=True)
    addr2_city =        models.CharField('City', max_length=255, blank=True, null=True)
    addr2_state =       models.CharField('State', blank=True, null=True, max_length=255)
    addr2_zip =         models.CharField('Zip Code', max_length=255, blank=True, null=True)
    addr2_country =     models.CharField('Country', max_length=255, blank=True, null=True)
    degree1 =           models.CharField('Degree', max_length=255, blank=True, null=True)
    major1 =            models.CharField('Major', max_length=255, blank=True, null=True)
    year1 =             models.IntegerField('Year', max_length=255, blank=True, null=True)
    school1 =           models.CharField('School', max_length=255, blank=True, null=True)
    degree2 =           models.CharField('Degree', max_length=255, blank=True, null=True)
    major2 =            models.CharField('Major', max_length=255, blank=True, null=True)
    year2 =             models.IntegerField('Year', max_length=255, blank=True, null=True)
    school2 =           models.CharField('School', max_length=255, blank=True, null=True)
    #tag_list =          models.CharField(max_length=255, blank=True)
    token =             models.CharField(max_length=255, blank=True, null=True)

    # User preferences
    do_not_email =      models.BooleanField(blank=True, default=False)
    preferred_comm =    models.CharField(blank=True, default="email", max_length=255, choices=(('email', 'Email'), ('phone','Phone'), ('mail', 'Mail')))

    # Internal use
    notes =             models.TextField(blank=True, null=True)

    tag_objects = tagging.managers.ModelTaggedItemManager()
    objects = models.Manager()

    def get_token(self):
        if not self.token:
            # Generate token
            salt = sha.new(str(random.random())).hexdigest()[:5]
            token = sha.new(salt+self.first_name).hexdigest()

            self.token = token
            self.save()

        return self.token
            
    def save(self):
        super(Contact, self).save()
        self.tags = self.tag_list

    def _get_tags(self):
        return Tag.objects.get_for_object(self)

    def _set_tags(self, tag_list):
        Tag.objects.update_tags(self, tag_list)

    tags = property(_get_tags, _set_tags)

    def __unicode__(self):
        return "%s %s (%s)" % (self.first_name, self.last_name, self.email)

    def generate_tag_list(self):
        return ", ".join([tag.name for tag in self.tags])

    def generate_and_save_tag_list(self):
        self.tag_list = self.generate_tag_list()
        super(Contact, self).save()

    tag_list = property(generate_tag_list, _set_tags)

# Contact attributes for advanced search dropdown
contactattrs = (
('full_name','Full Name'),
('first_name','First Name'),
('middle_initial','Middle Initial'),
('last_name','Last Name'),
('tag_list','Tags'),
('title','Title'),
('email','Email'),
('phone1','Primary Phone'),
('phone2','Secondary Phone'),
('fax1','Primary Fax'),
('fax2','Secondary Fax'),
('employer','Employer'),
('position','Position'),
('addr1_row1','Primary address row 1'),
('addr1_row2','Primary address row 2'),
('addr1_city','Primary address city'),
('addr1_state','Primary address state'),
('addr1_zip','Primary address zip'),
('addr1_country','Primary Country'),
('addr2_row1','Secondary address row 1'),
('addr2_row2','Secondary address row 2'),
('addr2_city','Secondary address city'),
('addr2_state','Secondary address state'),
('addr2_zip','Secondary address zip'),
('addr2_country','Secondary Country'),
('degree1','Primary Degree'),
('major1','Primary Major'),
('year1','Primary Graduation Year'),
('degree2','Secondary Degree'),
('major2','Secondary Major'),
('year2','Secondary Graduation Year'),
('do_not_email','Do Not Email'),
('preferred_comm','Preferred Comm'),
)


class ContactEditHistory(models.Model):
    contact = models.ForeignKey(Contact)
    user = models.ForeignKey(User, blank=True, null=True)
    event_date = models.DateTimeField(auto_now = True)
    message = models.CharField(max_length=255)


class ContactSavedSearch(models.Model):
    user = models.ForeignKey(User)
    name = models.CharField(max_length=255)
    contact_list = models.ManyToManyField(Contact)
    event_date = models.DateTimeField(auto_now = True)

    def __unicode__(self):
        return self.name
