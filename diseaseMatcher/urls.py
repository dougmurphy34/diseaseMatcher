from django.conf.urls import patterns, include, url
from diseaseMatcherApp import views

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'diseaseMatcher.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', include('diseaseMatcherApp.urls', namespace='diseaseMatcherApp'))

)
