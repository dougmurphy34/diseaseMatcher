from __future__ import absolute_import
import random
import json

#TODO: Replace get() calls with get_object_or_404
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.views import generic
from django.template import loader, context, RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Matches, Abstract, MatchLocations, MatchLocationsLookup

'''Principles of Views

--Less view code is better
--Never repeat code in views
--Views should handle presentation logic.  Try to keep business login in models (or forms if necessary).
--Keep views simple
--Use function-based views to write custom 403,404, and 500 handlers.
--Avoid complex nested-if blocks
--Keep mixins simpler (Mixin = abstract class.  When inheriting, always put mixin as left argument, django class as right argument.  All mixins inherit from 'object').
'''

#TODO: Can I set a global variable for DeepMatcher vs. Speedmatcher, and then modularize base.py?
#       Will probably still need to keep abstractDetail and process_matches separate.

# **********VIEWS**********
@login_required
def home_page(request):
    #create a welcome page
    template = loader.get_template('diseaseMatcherApp/index.html')

    user = request.user

    #pick a random abstract that this user hasn't seen before
    rnd = get_a_fresh_abstract(user)
    context = RequestContext(request, {'abstract_choice': rnd, 'user': user})

    return HttpResponse(template.render(context))


def start_registration(request):

    template = loader.get_template('diseaseMatcherApp/register.html')
    context = RequestContext(request)

    return HttpResponse(template.render(context))


class AbstractDetailView(generic.DetailView):
    #What the user will see while they search for disease names
    template_name = 'diseaseMatcherApp/abstractDetail.html'
    context_object_name = 'abstract'
    model = Abstract

    def a_function(self):
        return 99


@login_required
def logout_view(request):
    logout(request)

    return HttpResponseRedirect(reverse('login'))


@login_required
def play_again(request):
    template = loader.get_template('diseaseMatcherApp/playAgain.html')

    #TODO: Should this page be a modular version of the home page?
    #Maybe this becomes a post-login and post-game "get started" page that also shows recent activity,
    #   fulfilling the role of visually rewarding the player for completion
    user = request.user
    rnd = get_a_fresh_abstract(user)

    context = RequestContext(request,{'abstract_choice': rnd, 'user': user})

    return HttpResponse(template.render(context))


@login_required
def user_profile(request):
    template = loader.get_template('diseaseMatcherApp/userProfile.html')
    #get count of matches found, and in how many abstracts.  Maybe grid of title + matches?
    #user ranking (based on # matches, get all users with more matches, ranking = that + 1

    dict_of_work = {}

    this_user = request.user
    abstracts_worked_on = Matches.objects.filter(annotator_id=this_user.pk).values_list('abstract_id', flat=True).distinct()

    work_count = abstracts_worked_on.count

    my_rank = calculate_annotator_ranking(this_user)

    for abstract in abstracts_worked_on:
        match_name = Abstract.objects.get(pk=abstract).title
        match_count = Matches.objects.filter(abstract_id=abstract).count()
        dict_of_work[match_name] = match_count

    #TODO: Neither of these sorts is producing a working dictionary.  Maybe because it's a list of tuples?
    #sorted_dict_of_work = sorted(dict_of_work.items(), key=lambda x: x[1])
    #sorted_dict_of_work = sorted(dict_of_work.iteritems(), key=operator.itemgetter(1))


    context = RequestContext(request, {'abstractsWorkedOn': dict_of_work, 'abstractCount': work_count, 'rank': my_rank})

    return HttpResponse(template.render(context))


#*********TRANSACTIONS************

def process_registration(request):
    #See if registration already exists.  If yes + correct PW, login + index.html.  If yes + wrong PW, back to register
    username = request.POST['username']
    password = request.POST['password']

    user = authenticate(username=username, password=password)

    if user is not None:
        if user.is_active:
            login(request, user)
            return HttpResponseRedirect(reverse('homePage'))
        else:
            messages.success(request, "you're a user, but you have been disabled.")
            return HttpResponseRedirect(reverse('registration'))
    else:
        #If username isn't taken, create user and login
        try:
            new_user = User.objects.create_user(username=username, password=password)
            new_user.save()

        except:  #TODO: specify exception classes
            messages.error(request, "Failed on create new user.  Username is probably taken, try another.")
            return HttpResponseRedirect(reverse('registration'))

        try:
            #Now that the user has been created, we can authenticate with the user/pass we used to create them
            user_trying_again = authenticate(username=username, password=password)
            login(request, user_trying_again)
        except:
            messages.error(request, "Login failed after (possibly) creating user " + str(new_user))

        return HttpResponseRedirect(reverse('homePage'))


@login_required
def process_matches(request):
    #TODO: Build better test for process_matches

    #List of all words entered, in a space-delimited string
    try:
        which_abstract = request.POST.get('abstract_pk')
        answer_time_dict = json.loads(request.POST.get('userTypedMatches'))
        selected_text_time_dict = json.loads(request.POST.get('userHighlightedMatches'))
    except:
        #TODO: Better error handling for bad POST data
        return HttpResponse("Whoops!  Error.  I will handle this better later.")

    annotator_pk = User.objects.get(pk=request.user.id)
    abstract_pk = Abstract.objects.get(pk=which_abstract)

    answers = []

    for key in answer_time_dict:
        answers.append(key)

    for key in selected_text_time_dict:
        answers.append(key)

    for answer in answers:
        clean_answer = answer.strip()

        if 51 > len(clean_answer) > 0:
            if clean_answer in answer_time_dict:#TODO: This will cause a silent error when both ifs false (happens when user submits, then hits back button.  Prevent this?)

                this_match_time = answer_time_dict[clean_answer]

                offset_list = abstract_pk.match_location(clean_answer)

                if offset_list[0][0] != -1:
                    try:
                        #create Match record here.  Fields: abstract, annotator, text_matches, match_length, match_time
                        match = Matches.objects.create(abstract=abstract_pk, annotator = annotator_pk, text_matched=clean_answer,
                                                       match_length=len(clean_answer), match_time=this_match_time)

                        match.save()

                        for offset in offset_list:
                            #format of offset variable will be [HowDeepInTextAppears, MatchLocationAs0or1].  No match = [-1,-1]
                            if offset[0] != -1:
                                this_match_location = MatchLocationsLookup.objects.get(pk=offset[1])

                                #Create MatchLocations here.  Fields: match, match_location, match_offset

                                where_we_matched = MatchLocations.objects.create(match=match, match_location=this_match_location,
                                                                                 match_offset=offset[0])

                                where_we_matched.save()
                    except:
                        #TODO: Better error handling for database fail on match create
                        return HttpResponse("Something went screwy creating text-entered match records in the database.")
            elif clean_answer in selected_text_time_dict:
                try:
                    #process selected test.  Format {"selectedText" : {"seconds": 8, "titleText": 1, "offset": 32}}
                    match = Matches.objects.create(abstract=abstract_pk, annotator=annotator_pk, text_matched=clean_answer,
                                                   match_length=len(clean_answer), match_time=selected_text_time_dict[clean_answer]['secondsInt'])
                    match.save()
                except:
                    return HttpResponse("Error on create match for highlight text")
                try:
                    this_match_location = MatchLocationsLookup.objects.get(pk=selected_text_time_dict[clean_answer]['titleTextInt'])

                    where_we_matched = MatchLocations.objects.create(match=match, match_location=this_match_location,
                                                                     match_offset=selected_text_time_dict[clean_answer]['offset'])
                    where_we_matched.save()
                except:
                        error_string = "Something went screwy creating higlight-based match LOCATION records in the database.  " + str(clean_answer) + ", " + str(selected_text_time_dict[clean_answer])
                        return HttpResponse(error_string)

    return HttpResponseRedirect(reverse('diseaseMatcherApp:playAgain'))


#**********HELPER FUNCTIONS ******************
#TODO: These are not views.  Move them to a utils.py file, or to models.py

#This should be a function on the Annotator model, but "Annotator" is actually django.contrib.auth.models.User
def calculate_annotator_ranking(annotator):
    #helper function
    #takes an annotator, returns their rank among all annotators based on number of abstracts reviewed
    this_user_count = Matches.objects.filter(annotator=annotator).values_list('abstract_id', flat=True).distinct().count()
    better_users = 0

    all_users = User.objects.all()

    for user in all_users:
        temp_user_count = Matches.objects.filter(annotator=user).values_list('abstract_id', flat=True).distinct().count()
        if temp_user_count > this_user_count:
            better_users += 1

    return better_users + 1


def get_a_fresh_abstract(annotator):
    abstracts_seen = Matches.objects.filter(annotator=annotator).values_list('abstract_id')
    how_many_abstracts = Abstract.objects.all().count()

    if abstracts_seen == how_many_abstracts:
        return 0 #TODO: Handle this so that the user gets a "nice job, come back later" message

    while True:
        random_number = random.randint(1, how_many_abstracts)
        if random_number not in abstracts_seen:
            return random_number




