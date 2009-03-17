from django.conf.urls.defaults import *

urlpatterns = patterns('unitTest',   
    (r'^volunteer/createTestData/?$',           'volunteer.create'),
    (r'^volunteer/createTestData/bulk/?$',      'volunteer.bulkCreate'),
    (r'^npo/createTestData/?$',                 'npo.create'),
    (r'^npo/createTestData/bulk/?$',            'npo.bulkCreate'),
    (r'^countryCity/createTestData/?$',         'country.create'),
    (r'^createTestData/?$',                     'createTestData.showCreateTestData'),
    (r'^createTestData/kudo/?$',                'kudo.create'),
    # Clean Data
    (r'^cleanData/all/?$',                      'cleanData.cleanAll'),
)

urlpatterns += patterns('',
    # feedDiscovery
    (r'^feedDiscover/?$',                       'feedDiscover.unitTest'),
)
