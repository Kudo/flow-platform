from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()
from django.conf import settings

urlpatterns = patterns('',
    (r'^static/(?P<path>.*)$', 'django.views.static.serve',{'document_root': settings.MEDIA_ROOT}),
    (r'^event/',include('eventView.urls')),
    (r'^npo/',include('npoView.urls')),
    (r'^$','eventView.eventList.mainPage'),
)
