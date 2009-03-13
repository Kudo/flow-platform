from django.conf.urls.defaults import *

urlpatterns = patterns('npoView',   
    (r'^/?$',                       'npoList.show'),
    (r'^search/?$',                 'search.show'),
    # admin
    (r'^admin/?$', 'admin.mainPage'),
    # admin event management
    (r'^admin/editEvent/?$', 'editEvent.processEditEvent'),
    (r'^admin/addEvent/?$', 'addEvent.processAddEvent'),
    (r'^admin/authEvent/?$', 'authenticateEvent.submitAuthToken'),
    (r'^admin/handleAuthEvent/?$', 'authenticateEvent.handleEventAuth'),
    (r'^admin/listEvent/?$', 'eventMgmt.mainPage'),
    (r'^admin/cancelEvent/?$', 'eventMgmt.handleCancelEvent'),
    (r'^admin/selectVolunteer/?$', 'eventAdminValidate.volunteerShow'),
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
