from django.conf.urls.defaults import *

urlpatterns = patterns('eventView',
    (r'^viewEvent/?$',              'eventInfo.showEvent'),
    (r'^/?$',                       'eventList.mainPage'),
    (r'^applyEvent/?$',             'eventInfo.applyEvent'),
    (r'^mailToFriend/?$',           'eventInfo.mailToFriend'),
    (r'^applyYes/?$',               'eventInfo.applyYes'),
    (r'^applyNo/?$',                'eventInfo.applyNo'),
)
