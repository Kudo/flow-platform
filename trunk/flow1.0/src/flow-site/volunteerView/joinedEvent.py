#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import cgi
import datetime
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from google.appengine.ext import db
from google.appengine.api import users
import flowBase
from common import paging
from db.ddl import VolunteerProfile, VolunteerIm, NpoProfile

displayCount = 10
displayNpoEventCount = 3
diffDaysLimit = 14

dicStatusName = {
        "new registration": u'新註冊',
        "approving": u'審核中',
        "approval failed": u'審核不通過',
        "approved": u'審核通過',
        "involving": u'參與中',
        "partial involve": u'部分參與',
        "closed": u'活動已完成',
        "cancelled": u'活動取消',
        "abusive usage": u'遭檢舉不當活動',
        }

def redirect(request):
    return show(request, '')

def show(request, status, displayPhotoCount=8, displayBlogCount=6):
    user = flowBase.verifyVolunteer(request)
    if not user:
        return HttpResponseRedirect('/')

    if status == "history":
        events = db.GqlQuery('SELECT * FROM VolunteerEvent where volunteer_profile_ref = :1 and status = :2', user, "closed").fetch(1000)
    else:
        events = db.GqlQuery('SELECT * FROM VolunteerEvent where volunteer_profile_ref = :1 and status != :2', user, "closed").fetch(1000)
    eventCount = len(events)
    pageSet = paging.get(request.GET, eventCount, displayCount=displayCount)

    eventList = []
    for event in events:
        eventList.append(
         {'event_id':event.event_id,
         'event_name':event.event_profile_ref.event_name,
         'originator':event.event_profile_ref.npo_profile_ref.npo_name,
         'create_time':event.event_profile_ref.create_time.strftime('%Y-%m-%d %H:%M'),
         'start_time':event.event_profile_ref.start_time.strftime('%Y-%m-%d %H:%M'),
         'event_region':u','.join(event.event_profile_ref.event_region),
         'description':event.event_profile_ref.description,
         'registered_count':event.event_profile_ref.registered_count,
         'approved_count':event.event_profile_ref.approved_count,
         'volunteer_shortage':event.event_profile_ref.volunteer_shortage,
         'event_key':str(event.event_profile_ref.key()),
         'event_status':dicStatusName[event.status],
         }
         )

    '''
    now = datetime.datetime.now()
    npoCount = len(user.npo_profile_ref)
    pageSet = paging.get(request.GET, npoCount, displayCount=displayCount)
    npoList = [NpoProfile.get(user.npo_profile_ref[i]) for i in range(displayCount) if i < npoCount]
    for npo in npoList:
        npo.eventList = npo.event2npo.fetch(displayNpoEventCount)
        for event in npo.eventList:
            event.diffDays = (event.start_time - now).days
            event.upcoming = True if event.diffDays >= 0 and event.diffDays <= diffDaysLimit else False
            
        npo.memberCount = len(npo.members)
        npo.region = u', '.join(npo.service_region)
        npo.region = npo.region if len(npo.region) < 15 else npo.region[0:15] + u'...'
        if npo.brief_intro:
            npo.brief_intro = npo.brief_intro if len(npo.brief_intro) < 15 else npo.brief_intro[0:15] + u'...'
    '''
    
    # page: home, added by tom_chen... nasty workaround
    base = flowBase.getBase(request, 'volunteer')
    template_values = {
            'isSelf':                   True if base['user'] == user.volunteer_id else False,
            'base':                     base,
            'volunteerBase':            flowBase.getVolunteerBase(user),
            'page':                     'event',
            'eventList':                eventList,
            'pageSet':                  pageSet,
    }

    if status == "history":
        response = render_to_response('volunteer/joined_event_history.html', template_values)
    else:
        response = render_to_response('volunteer/joined_event.html', template_values)

    return response

