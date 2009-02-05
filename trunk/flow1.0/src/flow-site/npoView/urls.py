from django.conf.urls.defaults import *

urlpatterns = patterns('npoView',   
    (r'^editEvent/?$', 'editEvent.processEditEvent'),
    (r'^addEvent/?$', 'addEvent.processAddEvent'),
    (r'^listEvent/?$', 'eventMgmt.mainPage'),
    (r'^/?$', 'eventMgmt.mainPage'),
)
