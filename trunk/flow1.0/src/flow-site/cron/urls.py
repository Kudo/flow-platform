from django.conf.urls.defaults import *

urlpatterns = patterns('cron',
    (r'^5m/?$',       'cronJob.every5minutes'),
    (r'^hourly/?$',   'cronJob.hourly'),
    (r'^daily/?$',    'cronJob.daily'),
)
