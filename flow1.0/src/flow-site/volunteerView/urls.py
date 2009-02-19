from django.conf.urls.defaults import *

urlpatterns = patterns('volunteerView',   
    (r'^/?$',                           'list.list'),
    (r'^home/?$',                       'home.show'),
    (r'^profile/?$',                    'profile.show'),
    (r'^profile/edit/?$',               'profile.edit'),
    (r'^friend/?$',                     'friend.show'),
    (r'^friend/create/?$',              'friend.create'),
    (r'^friend/delete/?$',              'friend.delete'),
    (r'^space/?$',                      'space.show'),
    (r'^search/?$',                     'search.list'),
    # register
    (r'^register/?$',                   'register.step1'),
    (r'^register/step2/?$',             'register.step2'),
    (r'^register/step3/?$',             'register.step3'),
)
