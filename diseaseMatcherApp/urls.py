__author__ = 'Doug'

from django.conf.urls import url, patterns
from diseaseMatcherApp import views

urlpatterns = patterns('',
url(r'^$', views.AbstractListView.as_view(), name='abstractList')

)

