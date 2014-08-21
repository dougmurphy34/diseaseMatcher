from django.db import models
import datetime
from django.utils import timezone

# Create your models here.


#Raw data to be classified
class Abstract(models.Model):
    abstract_id = models.IntegerField()
    title = models.TextField(max_length=500)
    abstract_text = models.TextField(max_length=5000)
    pub_date = models.DateTimeField()

    def __unicode__(self):
        return self.title


#users
class Annotator(models.Model):
    #TODO: Implement password field (salt hash, etc)
    #TODO: Once login is implememted, disallow blank/null for last_entry_date
    username = models.TextField(max_length=25)
    last_entry_date = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return self.username


#Lookup table.  Current options: modifier, specific, class, composite
class MatchTypes(models.Model):
    type_name = models.TextField(max_length=15)

    def __unicode__(self):
        return self.type_name


#Each match is recorded separately, with match counts (for abstract-disease-location) gathered by query
class Matches(models.Model):
    abstract = models.ForeignKey(Abstract)
    annotator = models.ForeignKey(Annotator)
    #match_type = models.ForeignKey(MatchTypes)#future functionality
    text_matched = models.TextField(max_length=50)
    match_length = models.IntegerField()
    match_offset = models.IntegerField()