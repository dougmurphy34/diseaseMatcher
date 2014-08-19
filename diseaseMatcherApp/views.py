from django.shortcuts import render
from django.http import HttpResponse
from django.views import generic
from models import Abstract

# Create your views here.

class AbstractListView(generic.ListView):
    template_name = 'diseaseMatcherApp/abstractList.html'
    context_object_name = 'abstract_list'

    def get_queryset(self):
        return Abstract.objects.all()

class AbstractDetailView(generic.ListView):
    template_name = 'diseaseMatcherApp/abstractDetail.html'
    context_object_name = 'abstract'
    model = Abstract