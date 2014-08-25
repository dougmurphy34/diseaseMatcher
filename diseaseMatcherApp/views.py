from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.views import generic
from django.template import loader, context, RequestContext
from django.views.generic import detail
from django.core.urlresolvers import reverse
import random
from diseaseMatcherApp.models import Matches, Abstract

# Create your views here.


def home_page(request):
    #TODO: implement login
    #create a welcome page
    template = loader.get_template('diseaseMatcherApp/index.html')

    #pick a random abstract; is this the right place to be doing this?
    abstract_count = Abstract.objects.all().count()
    rnd = random.randint(1, abstract_count)
    context = RequestContext(request,{'abstract_choice':rnd})

    return HttpResponse(template.render(context))


def play_again(request):
    template = loader.get_template('diseaseMatcherApp/playAgain.html')

    #Should this page be a modular version of the home page?
    #Maybe this becomes a post-login and post-game "get started" page that also shows recent activity,
    #   fulfilling the role of visually rewarding the player for completion
    abstract_count = Abstract.objects.all().count()
    rnd = random.randint(1, abstract_count)
    context = RequestContext(request,{'abstract_choice':rnd})

    return HttpResponse(template.render(context))


def process_matches(request):
    #TODO: Build test for process_matches

    #List of all words entered, in a space-delimited string
    try:
        answer_string = request.POST.get('inputSoFar')
        answers = answer_string.split('\n')
        which_abstract = request.POST.get('abstract_pk')
    except:
        #TODO: Better error handling for this
        return HttpResponse("Whoops!  Error.  I will handle this better later.")

    annotator_pk = Annotator.objects.get(pk=1)  #placeholder.  Implement login system, then populate.  REQUIRES FAKE USER AFTER DB WIPE!
    abstract_pk = Abstract.objects.get(pk=which_abstract)

    for answer in answers:
        clean_answer = answer.strip()
        offset = abstract_pk.match_location(clean_answer)
        if offset != -1:
            if len(clean_answer) > 0:
                #TODO: Create client feedback in real time for answers - or, move to highlight-the-disease model
                match = Matches.objects.create(abstract=abstract_pk, annotator=annotator_pk, text_matched=clean_answer, match_length=len(clean_answer), match_offset=offset)
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

