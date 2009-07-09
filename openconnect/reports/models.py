from django.db import models


class Report(models.Model):
    name =              models.CharField("Name of this report", max_length=255)
    page_size =         models.CharField(default="Portrait", choices=(("Portrait", "Portrait"),("Landscape","Landscape")), max_length=8)
    first_name =        models.BooleanField("First Name")
    middle_initial =    models.BooleanField("Middle Initial")
    last_name =         models.BooleanField("Last Name")
    title =             models.BooleanField("Title")
    email =             models.BooleanField("Email")
    phone1 =            models.BooleanField("Primary Phone Number")
    phone2 =            models.BooleanField("Secondary Phone Number")
    fax1 =              models.BooleanField("Primary Fax")
    fax2 =              models.BooleanField("Secondary Fax")
    employer =          models.BooleanField("Employer")
    position =          models.BooleanField("Position")
    addr1_row1 =        models.BooleanField("Row 1")
    addr1_row2 =        models.BooleanField("Row 2")
    addr1_city =        models.BooleanField("City")
    addr1_state =       models.BooleanField("State")
    addr1_zip =         models.BooleanField("Zip Code")
    addr1_country =     models.BooleanField("Country")
    addr2_row1 =        models.BooleanField("Row 1")
    addr2_row2 =        models.BooleanField("Row 2")
    addr2_city =        models.BooleanField("City")
    addr2_state =       models.BooleanField("State")
    addr2_zip =         models.BooleanField("Zip Code")
    addr2_country =     models.BooleanField("Country")
    degree1 =           models.BooleanField("Degree")
    major1 =            models.BooleanField("Major")
    year1 =             models.BooleanField("Year")
    degree2 =           models.BooleanField("Degree")
    major2 =            models.BooleanField("Major")
    year2 =             models.BooleanField("Year")
    tag_list =          models.BooleanField("Tags")
    do_not_email =      models.BooleanField("Do Not Email")
    preferred_comm =    models.BooleanField("Preferred Comm")
    notes =             models.BooleanField("Notes")

    class Meta:
        permissions = (
            ("can_export", "Can Export Reports"),
        )


class SearchTerms(models.Model):
    field = models.CharField(max_length=255)
    condition = models.CharField(max_length=255)
    query = models.CharField(max_length=255)
    operator = models.CharField(max_length=255, blank=True, default="and")
    order = models.IntegerField()
    report = models.ForeignKey(Report, related_name="searchterms")
    
    class Meta:
        unique_together = ('report', 'order')
