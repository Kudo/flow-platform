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
from db.ddl import NpoAdmin
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

def memberList(request, npoid, message=None):
    npoProfile = NpoProfile.all().filter('npo_id = ', npoid).get()
    if npoProfile:
        
        npoMembershipList = list()
        for npoMember in npoProfile.members:
            npoMembershipList.append({
                'volunteer_profile': VolunteerProfile.get(npoMember), 
                'isAdmin':           (npoProfile.admins2npo.filter('volunteer_profile_ref = ', VolunteerProfile.get(npoMember)).count())
                })
        
        template_values = {
            'npoProfile':   npoProfile,
            'npoMembershipList': npoMembershipList,
            'message':      message,
            'page':         'members',
            'base':         flowBase.getBase(request, 'npo')
        }
        return render_to_response('npo/manage_managers.html', template_values)
    else:
        return HttpResponseRedirect(users.create_login_url(cgi.escape(request.path)))        

def manageMember(request, npoid):
    message = None
    npoProfile = NpoProfile.all().filter('npo_id = ', npoid).get()
    if npoProfile:
        volunteerid = None
        if 'volunteer_id' in request.POST:
            volunteerid = request.POST['volunteer_id']
        if 'operation' in request.POST:
            operation = request.POST['operation']
            if operation == 'add':
                #volunteerid is email address to the VolunteerProfile class
                volunteerProfile = VolunteerProfile.all().filter("volunteer_id =", users.User(volunteerid)).get()
                if volunteerProfile:
                    npoProfile.members.append(volunteerProfile.key()) #VolunteerProfile.all().filter("volunteer_id =", users.User(volunteerid)).get()
                    npoProfile.put()
                else:
                    message = volunteerid + ur' 不是一個有效的若水公益平台帳號，請檢查後重新輸入。'
            elif operation == 'set_manager':
                #volunteerid is email to the VolunteerProfile class
                volunteerProfile = VolunteerProfile.all().filter("volunteer_id =", users.User(volunteerid)).get()
                if volunteerProfile and volunteerProfile.key() in npoProfile.members:
                    npoManager = NpoAdmin(npo_profile_ref=npoProfile, admin_role="Main", volunteer_profile_ref=volunteerProfile)
                    npoManager.put()
                else:
                    #unexpected operation, do nothing.
                    pass
            elif operation == 'unset_manager':
                #volunteerid is email to the VolunteerProfile class
                volunteerProfile = VolunteerProfile.all().filter("volunteer_id =", users.User(volunteerid)).get()
                if volunteerProfile and volunteerProfile.key() in npoProfile.members:
                    npoManager = npoProfile.admins2npo.filter("volunteer_profile_ref = ", volunteerProfile).get()
                    if npoManager:
                        npoManager.delete()
                else:
                    #unexpected operation, do nothing.
                    pass
            elif operation == 'remove':
                #volunteerid is email  to the NpoAdmin class
                volunteerProfile = VolunteerProfile.all().filter("volunteer_id =", users.User(volunteerid)).get()
                if volunteerProfile and volunteerProfile.key() in npoProfile.members:
                    npoManager = npoProfile.admins2npo.filter("volunteer_id =", volunteerProfile.volunteer_id).get()
                    if npoManager:
                        npoManager.delete()
                    npoProfile.members.remove(volunteerProfile.key())
                    npoProfile.put()
                else:
                    # unexpected operation. do nothing 
                    pass
        return memberList(request, npoid, message)
    # invalid npoid, needing to loging as npoadmin, or other unexpected errors
    else:
        return HttpResponseRedirect(users.create_login_url(cgi.escape(request.path)))        

  
