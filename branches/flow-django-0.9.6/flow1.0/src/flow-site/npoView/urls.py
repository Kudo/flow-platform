from django.conf.urls.defaults import *

urlpatterns = patterns('npoView',   
    (r'^editEvent/?$',         'addEvent.modifyEvent'),
    (r'^addEvent/?$',               'addEvent.processAddEvent'),
    (r'^listEvent/?$',              'eventMgmt.mainPage'),
)
