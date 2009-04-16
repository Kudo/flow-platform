from django.conf.urls.defaults import *

urlpatterns = patterns('volunteerView',   
    # Local functions
    # Note that for each item that had 'key' matching should be placed in the last
    (r'^home/(?P<key>[^/]+)?/?$',                   'home.show'),
    (r'^joinedNpo/(?P<key>[^/]+)?/?$',              'joinedNpo.show'),
    (r'^profile/edit/?$',                           'profile.edit'),
    (r'^profile/(?P<key>[^/]+)?/?$',                'profile.show'),
    #(r'^friend/create/?$',                          'friend.create'),
    #(r'^friend/delete/?$',                          'friend.delete'),
    #(r'^friend/(?P<key>[^/]+)?/?$',                 'friend.show'),
    #(r'^space/video/create/?$',                     'space.videoCreate'),
    #(r'^space/video/delete/?$',                     'space.videoDelete'),
    #(r'^space/video/(?P<key>[^/]+)?/?$',            'space.videoShow'),
    #(r'^space/(?P<key>[^/]+)?/?$',                  'space.show'),
    #(r'^space/article/create/?$',                   'space.articleCreate'),
    #(r'^space/article/delete/?$',                   'space.articleDelete'),
    #(r'^space/article/saveUri/?$',                  'space.feedUriSave'),
    #(r'^space/article/(?P<key>[^/]+)?/?$',          'space.articleShow'),
    # Global functions
    (r'^/?$',                                       'volunteerList.show'),
    (r'^search/?$',                                 'search.show'),
    (r'^register/?$',                               'register.step1'),
    (r'^register/step2/?$',                         'register.step2'),
    (r'^register/step3/?$',                         'register.step3'),
)
