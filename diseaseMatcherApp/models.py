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
    last_entry_date = models.DateTimeField(default=timezone.now())

    def __unicode__(self):
        return self.username


class MatchTypes(models.Model):
    #Lookup table.  Current options: modifier, specific, class, composite
    type_name = models.TextField(max_length=15)

    def __unicode__(self):
        return self.type_name


class Matches(models.Model):
    annotator = models.ForeignKey(Annotator)
    match_type = models.ForeignKey(MatchTypes)
    text_matched = models.TextField(max_length=50)
    start_match = models.IntegerField()
    end_match = models.IntegerField()