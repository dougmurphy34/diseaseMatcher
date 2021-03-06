__author__ = 'Doug'

from django.conf.urls import url, patterns
from diseaseMatcherApp import views

urlpatterns = patterns('',
url(r'^$', views.home_page, name='homePage'),
url(r'^(?P<pk>\d+)/detail/$', views.AbstractDetailView.as_view(), name='abstractDetail'),
url(r'^process_matches/$', views.process_matches, name='processMatches'),
url(r'^play_again/$', views.play_again, name='playAgain'),
url(r'^user_profile/$', views.user_profile, name='userProfile')


)

