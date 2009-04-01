from django.conf.urls.defaults import *

urlpatterns = patterns('npoView',   
    (r'^/?$',                       'npoList.show'),
    (r'^search/?$',                 'search.show'),
    # admin
    (r'^(?P<npoid>[^/]+)/admin/?$',                  'admin.mainPage'),
    # admin event management
    (r'^admin/listEvent/?$',        'eventMgmt.mainPage'),
    (r'^admin/editEvent/?$',        'handleEvent.processEditEvent'),
    (r'^admin/addEvent/?$',         'handleEvent.processAddEvent'),
    (r'^admin/authEvent1/?$',       'authenticateEvent.submitAuthToken'),
    (r'^admin/authEvent2/?$',       'authenticateEvent.submitAuthToken'),
    (r'^admin/authEvent3/?$',       'authenticateEvent.handleEventAuth'),
    (r'^admin/cancelEvent/?$',      'eventMgmt.handleCancelEvent'),
    (r'^admin/volunteerList/?$',    'eventMgmt.volunteerList'),
    (r'^admin/volunteerListLong/?$',    'eventMgmt.volunteerListLong'),
    (r'^admin/selectVolunteer/?$',  'eventAdminValidate.volunteerShow'),
    (r'^admin/approveVolunteer/?$', 'eventAdminValidate.approveVolunteer'),
    (r'^(?P<npoid>[^/]+)/admin/members/manage/?$', 'admin.manageMember'),
    (r'^(?P<npoid>[^/]+)/admin/members/?$',        'admin.memberList'),
    # register
    (r'^register/?$',               'register.step1'),
    (r'^register/step2/?$',         'register.step2'),
    (r'^register/step3/?$',         'register.step3'),
    # profile
    (r'^npo_home.html$', 'npoProfile.showHome'),
    (r'^npo_info.html$', 'npoProfile.showInfo'),
    (r'^listEvents/?$',  'npoProfile.showEvents'),
    (r'^manage_edit_info.html$', 'npoProfile.edit'),
    (r'^npo_volunteers.html$', 'npoProfile.memberList'),
    # space
    (r'^(?P<npoid>[^/]+)/space/?$',                                 'space.show'),
    (r'^(?P<npoid>[^/]+)/space/video/create/?$',                    'space.videoCreate'),
    (r'^(?P<npoid>[^/]+)/space/video/delete/?$',                    'space.videoDelete'),
    (r'^(?P<npoid>[^/]+)/space/video/?$',                           'space.videoShow'),
    (r'^(?P<npoid>[^/]+)/space/article/create/?$',                  'space.articleCreate'),
    (r'^(?P<npoid>[^/]+)/space/article/delete/?$',                  'space.articleDelete'),
    (r'^(?P<npoid>[^/]+)/space/article/saveUri/?$',                 'space.feedUriSave'),
    (r'^(?P<npoid>[^/]+)/space/article/?$',                         'space.articleShow'),

)
