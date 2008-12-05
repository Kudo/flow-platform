from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^flowstaging/', include('flowstaging.foo.urls')),

    # showart pages
    (r'^showart/(?P<filename>.*)$', 'showart.showartAction'),
    # temp
    (r'^$', 'showart.showartAction', {'filename' : ''}),
)
