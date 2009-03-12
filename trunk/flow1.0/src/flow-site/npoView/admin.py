#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import datetime
import cgi
import re
import string
import random
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from google.appengine.ext import db
from google.appengine.api import users
from db.ddl import NpoProfile
from db.ddl import VolunteerProfile
from db.ddl import NpoContact
from db.ddl import NpoPhone
import flowBase

def mainPage(request):
    if 'npo_id' not in request.GET:
        return HttpResponseRedirect('/')
    else:
        npo_id = cgi.escape(request.GET['npo_id'])
        
    npoProfile = db.GqlQuery('SELECT * FROM NpoProfile WHERE npo_id = :1', npo_id).get()
    members = db.get(npoProfile.members)
    numOfMembers = len(members)
    
    # members showed in left column
    leftMembers = members[:]
    row1 = []
    for i in range(0, 3):
        if len(leftMembers) == 0:
            break
        row1.append(random.choice(leftMembers))
        leftMembers.remove(row1[i])
    
    row2 = []
    for i in range(0, 3):
        if len(leftMembers) == 0:
            break
        row2.append(random.choice(leftMembers))
        leftMembers.remove(row2[i])

    # prepare member list
    firstMember = None
    if (len(members) > 0):
        firstMember = members[0]
        del members[0]
            
    template_values = {
        'npoProfile': npoProfile,
        'firstMember': firstMember,
        'members': members,
        'numOfMembers': numOfMembers,
        'leftMembersRow1': row1,
        'leftMembersRow2': row2,
        'page': 'home',
        'base':flowBase.getBase(request, 'npo')
    }
    response = render_to_response('npo/admin_mainpage.html', template_values)
    return response
