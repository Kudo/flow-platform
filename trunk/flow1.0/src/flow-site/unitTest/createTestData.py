#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response

pages = [
        {   'uri'           : '/createTestData/', 
            'description'   : 'Create common test data, especially for event',
            'owner'         : 'Chien-Chih', 
        },
        {   'uri'           : '/unitTest/countryCity/createTestData/', 
            'description'   : 'Create country city test data',
            'owner'         : 'Kudo Chien', 
        },
        {   'uri'           : '/unitTest/volunteer/createTestData/', 
            'description'   : 'Create volunteer related test data',
            'owner'         : 'Kudo Chien', 
        },
        {   'uri'           : '/unitTest/volunteer/createTestData/bulk/', 
            'description'   : 'Bulk create volunteer test data',
            'owner'         : 'Kudo Chien', 
        },
        {   'uri'           : '/unitTest/volunteer/space/createTestData/', 
            'description'   : 'Create volunteer space test data',
            'owner'         : 'Kudo Chien', 
        },
        {   'uri'           : '/unitTest/volunteer/space/createTestData/bulk/', 
            'description'   : 'Bulk create volunteer space test data',
            'owner'         : 'Kudo Chien', 
        },
        {   'uri'           : '/unitTest/npo/createTestData/', 
            'description'   : 'Create npo related test data',
            'owner'         : 'Kudo Chien', 
        },
        {   'uri'           : '/unitTest/npo/createTestData/bulk/', 
            'description'   : 'Bulk create npo test data',
            'owner'         : 'Kudo Chien', 
        },
        {   'uri'           : '/unitTest/cleanData/all/', 
            'description'   : 'Clean all the ddl entities in datastore',
            'owner'         : 'Kudo Chien', 
        },

]


def showCreateTestData(request):
    return render_to_response('createTestData.html', {'pages' : pages})
