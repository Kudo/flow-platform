from django.conf.urls.defaults import *

urlpatterns = patterns('npoView',   
    (r'^editEvent/?$', 'editEvent.processEditEvent'),
    (r'^addEvent/?$', 'addEvent.processAddEvent'),
    (r'^listEvent/?$', 'eventMgmt.mainPage'),
    (r'^/?$', 'eventMgmt.mainPage'),
    # register
    (r'^register/?$',               'register.step1'),
    (r'^register/step2/?$',         'register.step2'),
    (r'^register/step3/?$',         'register.step3'),
)
