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
]


def showCreateTestData(request):
    return render_to_response('createTestData.html', {'pages' : pages})
