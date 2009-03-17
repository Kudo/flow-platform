from django.conf.urls.defaults import *

urlpatterns = patterns('aboutView',   
    (r'^(?P<filename>.*)$',            'about.show'),
)
