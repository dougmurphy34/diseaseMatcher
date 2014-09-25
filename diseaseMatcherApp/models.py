import re
import random
from datetime import datetime

from django.db import models
from django.contrib.auth.models import User
from django.core import serializers
from django.utils import timezone


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
    pub_date = models.DateField(default=datetime.now())

    def __unicode__(self):
        return self.title

    def gold_standard_match(self):
        """
        Abstract Detail View calls this to get the full list of GS matches
        This is passed to response.context as JSON
        """
        #TODO: Tighten up this data to only necessaries.  We don't need "model", for instance.  Is this removable?  values_list is only for fields inside GoldStandardMatch objects.
        gs_queryset = GoldStandardMatch.objects.filter(abstract=self)
        data = serializers.serialize('json', gs_queryset)

        return data

    def match_location(self, diseaseString):
        """
        search self.abstract_text and self.title for diseaseString
        return all locations of a match, or -1 if no match
        RETURN FORMAT: [[titleOrText, offset],[titleOrText2, offset2],etc.]
        Title Match = "1", Abstract Text Match = "2"
        """

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
    #TODO: This plus the user details model should become something other than a proxy class, most likely.
    #   A one-to-one?  Check Two Scoops ch. 18.

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


class UserDetails(TimeStampedModel):

    GENDERS = (
        (1, "Male"),
        (2, "Female")
    )

    EDUCATION_CHOICES = (
        (0, "Some elementary"),
        (1, "Finished elementary"),
        (2, "Some high school"),
        (3, "Finished high school"),
        (4, "Some community college"),
        (5, "Finished community college"),
        (6, "Some 4-year college"),
        (7, "Finished 4-year college"),
        (8, "Some masters program"),
        (9, "Finished masters program"),
        (10, "Some PhD program"),
        (11, "Finished PhD program")
    )

    PURPOSE_FOR_PLAYING_CHOICES = (
        (1, "Help Science"),
        (2, "Entertainment"),
        (3, "Knowledge is power"),
        (4, "Curiosity"),
        (5, "Other")
    )

    OCCUPATION_CHOICES = (
        (1, "Unemployed"),
        (2, "Retired"),
        (3, "Student"),
        (4, "Technical"),
        (5, "Science"),
        (6, "Computer"),
        (7, "Business"),
        (8, "Education"),
        (9, "Art"),
        (10, "Labor"),
        (11, "Finance"),
        (12, "Legal"),
        (13, "Other")
    )

    age = models.IntegerField(max_length=3, blank=True)
    gender = models.IntegerField(choices=GENDERS, blank=True)
    occupation = models.IntegerField(choices=OCCUPATION_CHOICES, blank=True)
    purpose_for_playing = models.IntegerField(choices=PURPOSE_FOR_PLAYING_CHOICES, blank=True)
    education = models.IntegerField(choices=EDUCATION_CHOICES, blank=True)


class GoldStandardMatch(models.Model):
    """
    This seems a bit like repeating myself with Matches, but differences:
    --GSMatch to location is 1-to-1, regular matches are one-to-many, hence GS does not use MatchLocations object
    --no annotator needed (always the same, the mysterious Mr. #6)
    --to match_time

    Hence, semi-duplication seems a better model than inheritance that shares only abstract, text_matched, and length
    """

    def __unicode__(self):
        return self.text_matched

    #This is violating "don't repeat yourself" (also in Match Locations), but I don't see a way around it.
    LOCATIONS = (
        (1, "Title"),
        (2, "Abstract Text")
    )

    annotation_id = models.IntegerField()  #Unclear if this is necessary
    abstract = models.ForeignKey(Abstract)
    text_matched = models.TextField(max_length=50)
    match_length = models.IntegerField()
    match_location = models.IntegerField(choices=LOCATIONS)
    match_offset = models.IntegerField()


class Matches(TimeStampedModel):

    """
    Thoughts on matches in general:

    Difference between text matching text, mouse highlight matching text/offset, and either matching GS make this model suboptimal
    depending on requirements (save non-GS matches?  Just record first text match for text matches?), might need to change model.

    One possibility: this is a concrete class, but it is inherited by another class that adds gold_standard_match
    This would be ideal if we needed to use the data (GS matches vs. text matches) for different thing.

    Closing thought: Real impact of this change would likely be so small, this may just be an intellectual exercise.
    Could get same effect with a WHERE clause when sorting out data.

    """

    def __unicode__(self):
        return self.text_matched

    abstract = models.ForeignKey(Abstract)
    annotator = models.ForeignKey(Annotator)  #User or Annotator?  This is a minor question.
    text_matched = models.TextField(max_length=50)
    match_length = models.IntegerField()
    match_time = models.IntegerField()  #How many seconds into the game did the user make the match?
    gold_standard_match = models.ForeignKey(GoldStandardMatch, blank=True, null=True)


class MatchLocations(TimeStampedModel):
    """
    For typed-in matches, each match is recorded separately, with abstract-disease-location
       gathered by Abstract.match_location(diseaseString)
    For highlighted matches, single match recorded based on location of highlighted text
    """

    LOCATIONS = (
        (1, "Title"),
        (2, "Abstract Text")
    )

    match = models.ForeignKey(Matches)
    match_location = models.IntegerField(choices=LOCATIONS)
    match_offset = models.IntegerField()
