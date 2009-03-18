from django.conf.urls.defaults import *

urlpatterns = patterns('volunteerView',   
    (r'^/?$',                           'volunteerList.show'),
    (r'^search/?$',                     'search.show'),
    (r'^home/?$',                       'home.show'),
    (r'^profile/?$',                    'profile.show'),
    (r'^profile/edit/?$',               'profile.edit'),
    (r'^friend/?$',                     'friend.show'),
    (r'^friend/create/?$',              'friend.create'),
    (r'^friend/delete/?$',              'friend.delete'),
    (r'^space/?$',                      'space.show'),
    (r'^space/video/?$',                'space.videoShow'),
    (r'^space/video/create/?$',         'space.videoCreate'),
    (r'^space/video/delete/?$',         'space.videoDelete'),
    (r'^space/article/?$',              'space.articleShow'),
    (r'^space/article/create/?$',       'space.articleCreate'),
    (r'^space/article/delete/?$',       'space.articleDelete'),
    (r'^space/article/saveUri/?$',      'space.feedUriSave'),
    # register
    (r'^register/?$',                   'register.step1'),
    (r'^register/step2/?$',             'register.step2'),
    (r'^register/step3/?$',             'register.step3'),
)