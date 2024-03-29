from django.conf.urls.defaults import *

urlpatterns = patterns('unitTest',   
    (r'^volunteer/createTestData/?$',           'volunteer.create'),
    (r'^volunteer/createTestData/bulk/?$',      'volunteer.bulkCreate'),
    (r'^volunteer/space/createTestData/?$',           'volunteer.spaceCreate'),
    (r'^volunteer/space/createTestData/bulk/?$',      'volunteer.bulkSpaceCreate'),
    (r'^npo/createTestData/?$',                 'npo.create'),
    (r'^npo/createTestData/bulk/?$',            'npo.bulkCreate'),
    (r'^countryCity/createTestData/?$',         'country.create'),
    (r'^createTestData/?$',                     'createTestData.showCreateTestData'),
    (r'^createTestData/kudo/?$',                'kudo.create'),
    # Utils
    (r'^cleanData/all/?$',                      'utils.cleanAll'),
    (r'^resetModelCount/?$',                    'utils.resetModelCount'),
)

urlpatterns += patterns('',
    # feedDiscovery
    (r'^feedDiscover/?$',                       'feedDiscover.unitTest'),
)
