from django.conf.urls.defaults import *

urlpatterns = patterns('npoView',   
    (r'^/?$',                       'npoList.show'),
    (r'^search/?$',                 'search.show'),
    # event
    (r'^editEvent/?$', 'editEvent.processEditEvent'),
    (r'^addEvent/?$', 'addEvent.processAddEvent'),
    (r'^authEvent/?$', 'authenticateEvent.submitAuthToken'),
    (r'^handleAuthEvent/?$', 'authenticateEvent.handleEventAuth'),
    (r'^listEvent/?$', 'eventMgmt.mainPage'),
    (r'^cancelEvent/?$', 'eventMgmt.showCancelEvent'),
    (r'^handleCancelEvent/?$', 'eventMgmt.handleCancelEvent'),
    (r'^selectVolunteer/?$', 'eventAdminValidate.volunteerShow'),
    # register
    (r'^register/?$',               'register.step1'),
    (r'^register/step2/?$',         'register.step2'),
    (r'^register/step3/?$',         'register.step3'),
    # profile
    (r'^npo_home.html$', 'npoProfile.showHome'),
    (r'^npo_info.html$', 'npoProfile.showInfo'),
    (r'^manage_edit_info.html$', 'npoProfile.edit'),
    (r'^npo_volunteers.html$', 'npoProfile.memberList'),
)
