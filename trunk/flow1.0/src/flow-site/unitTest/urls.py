from django.conf.urls.defaults import *

urlpatterns = patterns('unitTest',   
    (r'^volunteer/createTestData/?$',           'volunteer.create'),
    (r'^volunteer/createTestData/bulk/?$',      'volunteer.bulkCreate'),
    (r'^countryCity/createTestData/?$',         'country.create'),
    (r'^createTestData/?$',                     'createTestData.showCreateTestData'),
    (r'^createTestData/kudo/?$',                'kudo.create'),
)
