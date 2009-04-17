from django.conf.urls.defaults import *

urlpatterns = patterns('npoView',   
    (r'^/?$',                       'npoList.show'),
    (r'^search/?$',                 'search.show'),
    # admin
    (r'^(?P<npoid>[^/]+)/admin/?$',                  'admin.mainPage'),
    # admin event management
    (r'^(?P<npoid>[^/]+)/admin/listEvent/?$',        'eventMgmt.mainPage'),
    (r'^(?P<npoid>[^/]+)/admin/editEvent/?$',        'handleEvent.processEditEvent'),
    (r'^(?P<npoid>[^/]+)/admin/addEvent/?$',         'handleEvent.processAddEvent'),
    (r'^(?P<npoid>[^/]+)/admin/authEvent1/?$',       'authenticateEvent.submitAuthToken'),
    (r'^(?P<npoid>[^/]+)/admin/authEvent2/?$',       'authenticateEvent.submitAuthToken'),
    (r'^(?P<npoid>[^/]+)/admin/authEvent3/?$',       'authenticateEvent.handleEventAuth'),
    (r'^(?P<npoid>[^/]+)/admin/cancelEvent/?$',      'eventMgmt.handleCancelEvent'),
    (r'^(?P<npoid>[^/]+)/admin/volunteerList/?$',    'eventMgmt.volunteerList'),
    (r'^(?P<npoid>[^/]+)/admin/volunteerListLong/?$',    'eventMgmt.volunteerListLong'),
    (r'^(?P<npoid>[^/]+)/admin/selectVolunteer/?$',  'eventAdminValidate.volunteerShow'),
    (r'^(?P<npoid>[^/]+)/admin/approveVolunteer/?$', 'eventAdminValidate.approveVolunteer'),
    (r'^(?P<npoid>[^/]+)/admin/members/manage/?$', 'admin.manageMember'),
    (r'^(?P<npoid>[^/]+)/admin/members/?$',        'admin.memberList'),
    # register
    (r'^register/?$',               'register.step1'),
    (r'^register/step2/?$',         'register.step2'),
    (r'^register/step3/?$',         'register.step3'),
    # profile
    (r'^(?P<npoid>[^/]+)/?$',                               'npoProfile.showHome'),
    (r'^(?P<npoid>[^/]+)/events/?$',                        'npoProfile.showEventsRedir'),
    (r'^(?P<npoid>[^/]+)/events/(?P<status>[^/]+)/?$',      'npoProfile.showEvents'),
    (r'^(?P<npoid>[^/]+)/profile/?$',                       'npoProfile.showInfo'),
    (r'^(?P<npoid>[^/]+)/profile/edit/?$',                  'npoProfile.edit'),
    (r'^(?P<npoid>[^/]+)/volunteers/?$',                    'npoProfile.memberList'),
    # space
    (r'^(?P<npoid>[^/]+)/space/?$',                                 'space.show'),
    (r'^(?P<npoid>[^/]+)/space/album/create/?$',                    'space.albumCreate'),
    (r'^(?P<npoid>[^/]+)/space/album/delete/?$',                    'space.albumDelete'),
    (r'^(?P<npoid>[^/]+)/space/album/saveUri/?$',                   'space.albumUriSave'),
    (r'^(?P<npoid>[^/]+)/space/album/?$',                           'space.albumShow'),
    (r'^(?P<npoid>[^/]+)/space/video/create/?$',                    'space.videoCreate'),
    (r'^(?P<npoid>[^/]+)/space/video/delete/?$',                    'space.videoDelete'),
    (r'^(?P<npoid>[^/]+)/space/video/?$',                           'space.videoShow'),
    (r'^(?P<npoid>[^/]+)/space/article/create/?$',                  'space.articleCreate'),
    (r'^(?P<npoid>[^/]+)/space/article/delete/?$',                  'space.articleDelete'),
    (r'^(?P<npoid>[^/]+)/space/article/saveUri/?$',                 'space.feedUriSave'),
    (r'^(?P<npoid>[^/]+)/space/article/?$',                         'space.articleShow'),

)
