from django.conf.urls import patterns, include, url
from diseaseMatcherApp import views

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',

    url(r'^admin/', include(admin.site.urls)),
    url(r'^diseaseMatcher/', include('diseaseMatcherApp.urls', namespace='diseaseMatcherApp')),
    url(r'^$', views.home_page, name='homePage'),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'diseaseMatcherApp/login.html'}, name='login'),
    url(r'^accounts/registration/$', views.start_registration, name='registration'),
    url(r'^accounts/processRegistration/$', views.process_registration, name='process_registration'),
    url(r'^accounts/logout/$', views.logout_view, name='logout')

)
