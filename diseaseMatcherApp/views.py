from django.shortcuts import render
from django.http import HttpResponse
from django.views import generic
from models import Abstract
from django.template import loader, context, RequestContext
from django.views.generic import detail
import math
import random

# Create your views here.


def home_page(request):
    #create a welcome page
    template = loader.get_template('diseaseMatcherApp/index.html')

    #pick a random abstract; is this the right place to be doing this?
    rnd = random.randint(1,500)#CHANGE THIS - index to # of choices in database
    context = RequestContext(request,{'abstract_choice':rnd})

    return HttpResponse(template.render(context))

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
    slug_field = 'abstract_id'
    #detail.single

