from django.conf.urls.defaults import *

urlpatterns = patterns('utils',   
    (r'^youtubeParser/?$',              'youtubeParser.get'),
    (r'^feedParser/?$',                 'feedParser.get'),
)
