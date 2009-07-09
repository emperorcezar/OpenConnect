from datetime import datetime
from django.db import models
from django.contrib.auth.models import User
from contacts.models import Contact
from accounts.models import EmailAlias
from django.template.defaultfilters import wordcount, truncatewords
from utils.forms import CurrencyField, CurrencyInput
from utils.slugs import AutoSlugField

class Event(models.Model):
    title = models.CharField(max_length=255, unique=True)
    slug = AutoSlugField(max_length=255, populate_from='title')
    description = models.TextField()
    registrants = models.ManyToManyField(Contact, blank=True, null=True, related_name="registrants", through="Registrant")
    start = models.DateField()
    end = models.DateField()
    location = models.CharField(max_length=255)
    allowed_attendies = models.IntegerField(null=True, blank=True)
    last_edited = models.DateField(auto_now = True)
    payment_link = models.URLField(verify_exists=False)
    web_confirmation_message = models.TextField("Web Registration confirmation/pending message", blank=True, null=True)
    email_confirmation_message = models.TextField(blank=True, null=True)
    pending_message = models.TextField(blank=True, null=True)

    def get_price(self, contact):
        # check if prices exists
        if len(self.pricing_set.all()) == 0:
            return False

        # Get all prices that are valid for today
        queryset1 = self.pricing_set.filter(start__lt = datetime.today()) | self.pricing_set.filter(start = None)
        queryset2 = self.pricing_set.filter(end__gt = datetime.today()) | self.pricing_set.filter(end=None)
        queryset = queryset1 & queryset2
                
        registrant = Registrant.objects.get(event=self, contact=contact)
        price_list = []

        # Check if a discount code is given.
        prices = [i.price for i in queryset.filter(discount_code__iexact = registrant.discount_code)]
        price_list.extend(prices)

        # Check for tags
        for tag in contact.tags:
            prices = queryset.filter(tag_list__contains = tag.name)
            if len(prices) > 0:
                price_list.extend([i.price for i in prices])
                
        # Finally add any prices that don't have tags or discount codes
        price_list.extend([i.price for i in queryset.filter(tag_list='', discount_code='')])
        
        return min(price_list)

    def description_wordcount(self):
        return wordcount(self.description)

    def short_description(self):
        if self.description_wordcount() > 4:
            return truncatewords(self.description, 4)+' ...'
        else:
            return self.description

    def __unicode__(self):
        return self.title

class Registrant(models.Model):
    event = models.ForeignKey(Event)
    contact = models.ForeignKey(Contact)
    pending = models.BooleanField(default=True)
    discount_code = models.CharField(max_length=40, blank=True)

    def save(self):
        if self.id == None:
            # check for uniqueness
            results = Registrant.objects.filter(event = self.event, contact = self.contact)
            if len(results) > 0:
                return results[0]
        super(Registrant, self).save()

class Pricing(models.Model):
    event = models.ForeignKey(Event)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    discount_code = models.CharField(max_length = 40, blank=True)
    tag_list = models.CharField(max_length=255, blank=True)
    start = models.DateField(blank=True, null=True)
    end = models.DateField(blank=True, null=True)
