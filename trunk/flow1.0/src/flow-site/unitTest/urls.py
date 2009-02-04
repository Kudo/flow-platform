from django.conf.urls.defaults import *

urlpatterns = patterns('unitTest',   
    (r'^volunteer/createTestData/?$',           'volunteer.create'),
    (r'^countryCity/createTestData/?$',         'country.create'),
)
