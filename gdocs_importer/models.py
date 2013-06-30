from django.db import models


class Homicide(models.Model):
    address = models.CharField(max_length=100, blank=True, null=True)
    date_time = models.DateTimeField(blank=True, null=True)
    location = models.CharField(max_length=50, blank=True, null=True)
    neighborhood = models.CharField(max_length=100, blank=True, null=True)
    age = models.IntegerField(blank=True, null=True)
    gender = models.CharField(max_length=7, blank=True, null=True)
    race = models.CharField(max_length=20, blank=True, null=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    cause = models.CharField(max_length=20, blank=True, null=True)
    story_url = models.URLField(blank=True, null=True)
    rd_number = models.CharField(max_length=15, blank=True, null=True)
    charges_url = models.URLField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.address

    def has_changed(self, field):
        if self.pk is not None:
            orig = Homicide.objects.get(pk=self.pk)
            if getattr(orig, field) != getattr(self, field):
                return True
        return False
