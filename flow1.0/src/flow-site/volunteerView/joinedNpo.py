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

def show(request, key, displayPhotoCount=8, displayBlogCount=6):
    user = flowBase.verifyVolunteer(request, key)
    if not user:
        return HttpResponseRedirect('/')

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
    
    # page: home, added by tom_chen... nasty workaround
    template_values = {
            'base':                     flowBase.getBase(request, 'volunteer'),
            'volunteerBase':            flowBase.getVolunteerBase(user),
            'page':                     'npo',
            'npoList':                  npoList,
            'pageSet':                  pageSet,
    }
    response = render_to_response('volunteer/joined_npo.html', template_values)

    return response

