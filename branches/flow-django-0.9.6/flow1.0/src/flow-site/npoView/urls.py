from django.conf.urls.defaults import *

urlpatterns = patterns('npoView',   
    (r'^npoEventAction/?$',         'addEvent.modifyEvent'),
    (r'^addEvent/?$',               'addEvent.processAddEvent'),
    (r'^listEvent/?$',              'eventMgmt.mainPage'),
)
