import re
import random
from datetime import datetime

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
#TODO: Can I make an Annotator model that inherits from the default User model?  I could put functions here.  See Two Scoops Ch. 18.


#ABSTRACT CLASSES
class TimeStampedModel(models.Model):
    """
    An abstract base class model that provides self-updating
    ''created'' and ''modified'' fields.
    """

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


#Scientific abstracts to be classified
class Abstract(models.Model):
    abstract_id = models.IntegerField()
    title = models.TextField(max_length=500)
    abstract_text = models.TextField(max_length=5000)
    pub_date = models.DateTimeField(default=datetime.now)

    def __unicode__(self):
        return self.title

    def match_location(self, diseaseString):
        #search self.abstract_text and self.title for diseaseString
        #return all locations of a match, or -1 if no match
        #RETURN FORMAT: [[titleOrText, offset],[titleOrText2, offset2],etc.]
        #Title Match = "1", Abstract Text Match = "2"

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


#Extends django.auth.models.User using a proxy model to add useful methods
class Annotator(User):
    #TODO: If i get this working, take calculate_annotator_ranking out of views.py

    class Meta:
        proxy = True

    def calculate_ranking(self):
        #returns rank among all annotators based on number of abstracts reviewed
        this_user_count = Matches.objects.filter(annotator=self).values_list('abstract_id', flat=True).distinct().count()
        better_users = 0

        all_users = User.objects.all()

        for user in all_users:
            temp_user_count = Matches.objects.filter(annotator=user).values_list('abstract_id', flat=True).distinct().count()
            if temp_user_count > this_user_count:
                better_users += 1

        return better_users + 1

    def get_a_fresh_abstract(self):
        abstracts_seen = Matches.objects.filter(annotator=self).values_list('abstract_id')
        how_many_abstracts = Abstract.objects.all().count()

        if abstracts_seen == how_many_abstracts:
            return 0 #TODO: Handle this so that the user gets a "nice job, come back later" message

        while True:
            random_number = random.randint(1, how_many_abstracts)
            if random_number not in abstracts_seen:
                return random_number


#Lookup table.  Describes which field had the text match.  Current options: Title, Abstract Text.
class MatchLocationsLookup(models.Model):
    location = models.TextField(max_length=25)


#For typed-in matches, each match is recorded separately, with abstract-disease-location gathered by query
#For highlighted matches, single match recorded based on location of higlighted text
class Matches(TimeStampedModel):

    def __unicode__(self):
        return self.text_matched

    abstract = models.ForeignKey(Abstract)
    annotator = models.ForeignKey(User)
    text_matched = models.TextField(max_length=50)
    match_length = models.IntegerField()
    match_time = models.IntegerField()  #How many seconds into the game did the user make the match?


class MatchLocations(TimeStampedModel):
    match = models.ForeignKey(Matches)
    match_location = models.ForeignKey(MatchLocationsLookup)
    match_offset = models.IntegerField()


class GenderLookup(models.Model):
    gender = models.TextField(max_length=6)


class EducationLookup(models.Model):
    education_level = models.TextField(max_length=15)


class PurposeForPlayingLookup(models.Model):
    purpose = models.TextField(max_length=20)


class OccupationLookup(models.Model):
    occupation = models.TextField(max_length=50)


class UserDetails(TimeStampedModel):
    age = models.IntegerField(max_length=3, blank=True)
    gender = models.ForeignKey(GenderLookup, blank=True)
    occupation = models.ForeignKey(OccupationLookup, blank=True)
    purpose_for_playing = models.ForeignKey(PurposeForPlayingLookup, blank=True)
    education = models.ForeignKey(EducationLookup, blank=True)