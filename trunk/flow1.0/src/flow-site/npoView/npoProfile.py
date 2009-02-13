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
#from db.ddl import VolunteerProfile

def edit(request):
    if request.method == 'POST':
        npoProfile = db.GqlQuery('SELECT * FROM NpoProfile WHERE npo_id = :1', 'NPO:0').get()
        npoProfile.founder = request.POST['txtFounder']
        npoProfile.put()
        return HttpResponseRedirect("npo_info.html?npo_id=NPO:0")
    else:
        if 'npo_id' not in request.GET:
            return HttpResponseRedirect('/')
        else:
            npo_id = cgi.escape(request.GET['npo_id'])
        
        npoProfile = db.GqlQuery('SELECT * FROM NpoProfile WHERE npo_id = :1', npo_id).get()
  
        template_values = {
                'path': request.path,
                'npoProfile': npoProfile,
         }
        response = render_to_response('npo/manage_edit_info.html', template_values)
        return response    

def memberList(request):
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
    firstMember = members[0]
    del members[0]
            
    template_values = {
        'npoProfile': npoProfile,
        'firstMember': firstMember,
        'members': members,
        'numOfMembers': numOfMembers,
        'leftMembersRow1': row1,
        'leftMembersRow2': row2,
    }
    response = render_to_response('npo/npo_volunteers.html', template_values)
    return response

def showHome(request):
    if 'npo_id' not in request.GET:
        return HttpResponseRedirect('/')
    else:
        npo_id = cgi.escape(request.GET['npo_id'])
        
#    user = users.User("john_doe@gmail.com")
#    now = datetime.datetime.utcnow()
#    npo = NpoProfile(npo_name="Holy Shoot",founder="Rick Wang", google_acct=user, country="ROC", postal="104", state="Taiwan", city="Taipei",
#                     district="Nangang", founding_date=datetime.date(1980, 1, 1), authority="GOV", tag=["wild lives", "marines"],
#                     status="new application", docs_link=["Timbuck2"], npo_rating=1, create_time=now, update_time=now, news_list=[db.Text(u"最新消息第一條"), db.Text(u"最新消息第二條"), db.Text(u"最新消息第三條")])
# 
#    npo.put()
        
#    user      = users.User("jane_doe@gmail.com")
#    now       = datetime.datetime.utcnow()
#    volunteer = VolunteerProfile(volunteer_id=user, id_no="A123456789", volunteer_last_name="Doe", volunteer_first_name="Jacy", gmail=user.email(),
#                                 date_birth=datetime.date(1970, 2, 1), expertise=["PR"], sex="Female", phone_no="02-1234-5678", resident_country="ROC",
#                                 resident_postal="104", resident_state="Taiwan", resident_city="Taipei", resident_district="Shilin",
#                                 prefer_region=[], prefer_zip=[], prefer_target=[], prefer_field=[], prefer_group=[],
#                                 create_time=now, update_time=now, volunteer_rating=80, status="normal" , search_text=u"測試中文字 test. ngram 屋啦啦 中英文English")
#
#    volunteer.put()
#    npoProfile = db.GqlQuery('SELECT * FROM NpoProfile WHERE npo_id = :1', npo_id).get()
#    npoProfile.members.append(volunteer.key())
#    
#    npoProfile.put()

    npoProfile = db.GqlQuery('SELECT * FROM NpoProfile WHERE npo_id = :1', npo_id).get()
    members = db.get(npoProfile.members)
    
    # recently attended members
    recentMembers = members[:]
    latestMember = recentMembers[-1]
    recentMembers = recentMembers[-5:-1]
    recentMembers.reverse()
    
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
    
    template_values = {
            'npoProfile': npoProfile,
            'recentMembers': recentMembers,
            'latestMember': latestMember,
            'leftMembersRow1': row1,
            'leftMembersRow2': row2,
            'numOfMembers': len(members),
     }
    response = render_to_response('npo/npo_home.html', template_values)
    return response

def showInfo(request):
    if 'npo_id' not in request.GET:
        return HttpResponseRedirect('/')
    else:
        npo_id = cgi.escape(request.GET['npo_id'])

    npoProfile = db.GqlQuery('SELECT * FROM NpoProfile WHERE npo_id = :1', npo_id).get()

    template_values = {
            'npoProfile': npoProfile,
     }
    response = render_to_response('npo/npo_info.html', template_values)
    return response

def leftColumn(request):
    if 'npo_id' not in request.GET:
        return HttpResponseRedirect('/')
    else:
        npo_id = cgi.escape(request.GET['npo_id'])
        
    npoProfile = db.GqlQuery('SELECT * FROM NpoProfile WHERE npo_id = :1', npo_id).get()
    members = db.get(npoProfile.members)
        
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
        
    template_values = {
            'npoProfile': npoProfile,
            'leftMembersRow1': row1,
            'leftMembersRow2': row2,
            'numOfMembers': len(members),
     }
    response = render_to_response('npo/profile_leftcolumn.html', template_values)
    return response
    