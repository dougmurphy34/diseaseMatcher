from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.views import generic
from django.template import loader, context, RequestContext
from django.core.urlresolvers import reverse
import random
from diseaseMatcherApp.models import Matches, Abstract, MatchLocations, MatchLocationsLookup
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import json


# **********VIEWS**********
@login_required
def home_page(request):
    #create a welcome page
    template = loader.get_template('diseaseMatcherApp/index.html')

    user = request.user

    #pick a random abstract
    abstract_count = Abstract.objects.all().count()
    rnd = random.randint(1, abstract_count)
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
    abstract_count = Abstract.objects.all().count()
    rnd = random.randint(1, abstract_count)
    user = request.user
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

    #Neither of these sorts is producing a working dictionary.  Maybe because it's a list of tuples?
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
        answer_string = request.POST.get('inputSoFar')
        answers = answer_string.split('\n')
        which_abstract = request.POST.get('abstract_pk')
        answer_time_dict = json.loads(request.POST.get('userMatches'))
    except:
        #TODO: Better error handling for bad POST data
        return HttpResponse("Whoops!  Error.  I will handle this better later.")

    annotator_pk = User.objects.get(pk=request.user.id)
    abstract_pk = Abstract.objects.get(pk=which_abstract)

    #TODO: Create client feedback in real time for answers - or, move to highlight-the-disease model
    for answer in answers:
        clean_answer = answer.strip()

        if 51 > len(clean_answer) > 0:
            this_match_time = answer_time_dict[clean_answer]

            #TODO: Prevent duplicate matches
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
                    return HttpResponse("Something went screwy creating match records in the database.")

    return HttpResponseRedirect(reverse('diseaseMatcherApp:playAgain'))


#**********HELPER FUNCTIONS ******************

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



