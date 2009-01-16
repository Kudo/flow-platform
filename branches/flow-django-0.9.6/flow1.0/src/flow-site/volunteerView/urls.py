from django.conf.urls.defaults import *

urlpatterns = patterns('volunteerView',   
    (r'^profile/?$',                  'profile.show'),
    (r'^profile/edit/?$',             'profile.edit'),
    (r'^friend/?$',                   'friend.show'),
    (r'^friend/create/?$',            'friend.create'),
    (r'^friend/delete/?$',            'friend.delete'),
    (r'^space/?$',                    'space.show'),
)
