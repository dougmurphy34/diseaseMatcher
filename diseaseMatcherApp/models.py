from django.db import models
from django.contrib.auth.models import User
import re
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

    def match_location(self, diseaseString):
        #search self.abstract_text for diseaseString
        #return the first (all) locations of a match, or -1 if no match
        match = re.search(diseaseString, self.abstract_text)
        match2 = re.search(diseaseString, self.title)

        #TODO: This returns terrible data - the offset could be from the title or from the text, it's not recorded anywhere
        if match:
            return match.start()
        elif match2:
            return match2.start()
        else:
            return -1

#Removing Annotator in favor of built-in Users model
'''
class Annotator(models.Model):
    #TODO: Implement password field (salt hash, etc)
    #TODO: Remove last_entry_date
    username = models.TextField(max_length=25)
    password = models.

    def __unicode__(self):
        return self.username
'''

#Lookup table.  Current options: modifier, specific, class, composite
class MatchTypes(models.Model):
    type_name = models.TextField(max_length=15)

    def __unicode__(self):
        return self.type_name


#Each match is recorded separately, with match counts (for abstract-disease-location) gathered by query
class Matches(models.Model):
    abstract = models.ForeignKey(Abstract)
    annotator = models.ForeignKey(User)
    #match_type = models.ForeignKey(MatchTypes)#future functionality
    text_matched = models.TextField(max_length=50)
    match_length = models.IntegerField()
    match_offset = models.IntegerField()