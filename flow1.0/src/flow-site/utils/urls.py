from django.conf.urls.defaults import *

urlpatterns = patterns('utils',   
    (r'^picasaWebParser/?$',            'picasaWebParser.get'),
    (r'^youtubeParser/?$',              'youtubeParser.get'),
    (r'^feedParser/?$',                 'feedParser.get'),
)
