from django.conf.urls.defaults import *

urlpatterns = patterns('npoView',   
    (r'^addEvent/?$',               'addEvent.processAddEvent'),
    (r'^listEvent/?$',              'eventMgmt.mainPage'),
)
