from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.views import generic
from django.template import loader, context, RequestContext
from django.core.urlresolvers import reverse
import random
from diseaseMatcherApp.models import Matches, Abstract, MatchLocations
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import json

# Create your views here.


@login_required
def home_page(request):
    #create a welcome page
    template = loader.get_template('diseaseMatcherApp/index.html')

    user = request.user

    #pick a random abstract; is this the right place to be doing this?
    abstract_count = Abstract.objects.all().count()
    rnd = random.randint(1, abstract_count)
    context = RequestContext(request, {'abstract_choice': rnd, 'user': user})

    return HttpResponse(template.render(context))


def start_registration(request):

    template = loader.get_template('diseaseMatcherApp/register.html')
    context = RequestContext(request)

    return HttpResponse(template.render(context))

@login_required
def logout_view(request):
    logout(request)

    return HttpResponseRedirect(reverse('login'))

@login_required
def play_again(request):
    template = loader.get_template('diseaseMatcherApp/playAgain.html')

    #Should this page be a modular version of the home page?
    #Maybe this becomes a post-login and post-game "get started" page that also shows recent activity,
    #   fulfilling the role of visually rewarding the player for completion
    abstract_count = Abstract.objects.all().count()
    rnd = random.randint(1, abstract_count)
    user = request.user
    context = RequestContext(request,{'abstract_choice': rnd, 'user': user})

    return HttpResponse(template.render(context))


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
            messages.success(request, "You created user " + str(new_user))
        except:
            messages.error(request, "Failed on create new user.  Username is probably taken, try another.")
            return HttpResponseRedirect(reverse('registration'))

        try:
            login(request, new_user)
        except:
            messages.error(request, "Login failed after (possibly) creating user")

        return HttpResponseRedirect(reverse('homePage'))

@login_required
def process_matches(request):
    #TODO: Build better test for process_matches

    #List of all words entered, in a space-delimited string
    try:
        answer_string = request.POST.get('inputSoFar')
        answers = answer_string.split('\n')
        which_abstract = request.POST.get('abstract_pk')
    except:
        #TODO: Better error handling for this
        return HttpResponse("Whoops!  Error.  I will handle this better later.")

    annotator_pk = User.objects.get(pk=request.user.id)
    abstract_pk = Abstract.objects.get(pk=which_abstract)
    answer_time_dict = json.loads(request.POST.get('userMatches'))

    for answer in answers:
        clean_answer = answer.strip()

        if len(clean_answer) > 0:
            this_match_time = answer_time_dict[clean_answer]

            offset_list = abstract_pk.match_location(clean_answer)

            for offset in offset_list:
                #format of offset variable will be [HowDeepInTextAppears, MatchLocationAs0or1].  No match = [-1,-1]
                if offset[0] != -1:
                    this_match_location = MatchLocations.objects.get(pk=offset[1])

                    #TODO: Create client feedback in real time for answers - or, move to highlight-the-disease model
                    match = Matches.objects.create(
                        abstract=abstract_pk, annotator=annotator_pk, text_matched=clean_answer,
                        match_length=len(clean_answer), match_offset=offset[0], match_location=this_match_location,
                        match_time=this_match_time)
                    match.save()

    #to find csrfmiddlewaretoken for implementation testing
    #return HttpResponse(request.POST.get('csrfmiddlewaretoken'))

    return HttpResponseRedirect(reverse('diseaseMatcherApp:playAgain'))


class AbstractListView(generic.ListView):
    #All abstracts in the DB in one big list - for testing, not part of the app
    template_name = 'diseaseMatcherApp/abstractList.html'
    context_object_name = 'abstract_list'

    def get_queryset(self):
        return Abstract.objects.all()


class AbstractDetailView(generic.DetailView):
    #What the user will see while they search for disease names
    template_name = 'diseaseMatcherApp/abstractDetail.html'
    context_object_name = 'abstract'
    model = Abstract

