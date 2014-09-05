from django.db import models
from django.contrib.auth.models import User
import re
import datetime
from django.utils import timezone


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
        #return all locations of a match, or -1 if no match
        #NEW RETURN FORMAT: [[titleOrText, offset],[titleOrText2, offset2],etc.]
        #Title Match = "1", Abstract Text Match = "2"

        #TODO: This code now slow.  Speed it up.
        text_matches = re.finditer(diseaseString, self.abstract_text)
        title_matches = re.finditer(diseaseString, self.title)

        list_of_results = []

        for match in text_matches:
            list_of_results += [[match.start(), 2]]

        for match in title_matches:
            list_of_results += [[match.start(), 1]]

        if len(list_of_results) > 0:
            return list_of_results
        else:
            return [[-1, -1]]

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


#Lookup table.  Not yet implemented.  Current options: modifier, specific, class, composite
class MatchTypes(models.Model):
    type_name = models.TextField(max_length=15)

    def __unicode__(self):
        return self.type_name


#Lookup table.  Describes which field had the text match.  Current options: Title, Abstract Text.
class MatchLocations(models.Model):
    location = models.TextField(max_length=25)


#Each match is recorded separately, with match counts (for abstract-disease-location) gathered by query
class Matches(models.Model):
    abstract = models.ForeignKey(Abstract)
    annotator = models.ForeignKey(User)
    #match_type = models.ForeignKey(MatchTypes)#future functionality
    text_matched = models.TextField(max_length=50)
    match_length = models.IntegerField()
    match_offset = models.IntegerField()
    match_location = models.ForeignKey(MatchLocations)
    match_time = models.IntegerField()  #How many seconds into the game did the user make the match?
