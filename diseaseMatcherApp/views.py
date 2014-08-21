from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.views import generic
from models import Abstract
from django.template import loader, context, RequestContext
from django.views.generic import detail
from django.core.urlresolvers import reverse
import random
from diseaseMatcherApp.models import Matches, Abstract, Annotator

# Create your views here.


def home_page(request):
    #TODO: implement login
    #create a welcome page
    template = loader.get_template('diseaseMatcherApp/index.html')

    #pick a random abstract; is this the right place to be doing this?
    rnd = random.randint(1,500)#TODO: index to # of choices in database
    context = RequestContext(request,{'abstract_choice':rnd})

    return HttpResponse(template.render(context))

def process_matches(request):
    #TODO: Build test for process_matches

    #List of all words entered, in a space-delimited string
    try:
        answerString = request.POST.get('inputSoFar')
        answers = answerString.split()
        which_abstract = request.POST.get('abstract_pk')
    except:
        #TODO: Better error handling for this
        return HttpResponse("Whoops!  Error.  I will handle this better later.")

    #TODO: Handle multi-word answers
    #TODO: Don't accept words that aren't in abstract

    x = 0

    annotator_pk = Annotator.objects.get(pk=1)#placeholder.  Implement login system, then populate.  REQUIRES FAKE USER AFTER DB WIPE!
    abstract_pk = Abstract.objects.get(pk=which_abstract)#placeholder.  Pass this in invisible field in form?
    offset = 1#placeholder

    for answer in answers:
        #I will need: abstract pk, annotator pk, answer
        x += 1 #for testing
        match = Matches.objects.create(abstract=abstract_pk, annotator=annotator_pk, text_matched=answer, match_length=len(answer), match_offset=offset)
        match.save()

    return HttpResponse(answerString + ", " + str(x))
    #return HttpResponseRedirect(reverse('diseaseMatcherApp:homePage'))#TODO: Point this at a "Thank you, play again?" page

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

