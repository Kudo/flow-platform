from django.conf.urls.defaults import *

urlpatterns = patterns('adminView',
    (r'^/?$',                        'siteAdmin.adminAccountList'),
    (r'^accounts/add',               'siteAdmin.addAdmin'),
    (r'^accounts/remove',            'siteAdmin.removeAdmin'),
    (r'^accounts/?$',                'siteAdmin.adminAccountList'),
    (r'^npo/changeStatus',           'siteAdmin.changeNpoStatus'),
    (r'^npo/?$',                     'siteAdmin.npoList'),
    (r'^volunteer/changeStatus',     'siteAdmin.changeVolunteerStatus'),
    (r'^volunteer/?$',               'siteAdmin.volunteerList'),
    (r'^event/changeStatus',         'siteAdmin.changeEventStatus'),
    (r'^event/?$',                   'siteAdmin.eventList'),
)
