from django.conf.urls.defaults import *

urlpatterns = patterns('eventView',
    (r'^viewEvent/?$',              'eventInfo.showEvent'),
    (r'^/?$',                       'eventList.mainPage'),
)
