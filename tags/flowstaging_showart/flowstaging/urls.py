from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()
from django.conf import settings

urlpatterns = patterns('',
    # Example:
    # (r'^flowstaging/', include('flowstaging.foo.urls')),
    (r'^static/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT}),
    # showart pages
    (r'^showart/(?P<filename>.*)$', 'showart.showartAction'),
    # temp
    (r'^/?$', 'showart.showartAction', {'filename' : ''}),
)
