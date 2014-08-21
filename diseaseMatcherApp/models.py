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
    username = models.TextField(max_length=25)
    last_entry_date = models.DateTimeField()
    #TODO: Implement password field (salt hash, etc)
    def __unicode__(self):
        return self.username


#Lookup table.  Current options: modifier, specific, class, composite
class MatchTypes(models.Model):
    type_name = models.TextField(max_length=15)

    def __unicode__(self):
        return self.type_name


#what we are collecting
class Matches(models.Model):
    annotator = models.ForeignKey(Annotator)
    match_type = models.ForeignKey(MatchTypes)
    text_matched = models.TextField(max_length=50)
    #TODO: move to length/offset model Ben used for MechTurk XML
    start_match = models.IntegerField()
    end_match = models.IntegerField()