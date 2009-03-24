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
import atom.url
import gdata.alt.appengine
import gdata.photos, gdata.photos.service
import gdata.youtube, gdata.youtube.service
import flowBase
from db.ddl import VolunteerProfile, VolunteerIm, NpoProfile

displayNpoCount = 10
displayNpoEventCount = 3
diffDaysLimit = 14

def show(request, displayPhotoCount=8, displayBlogCount=6):
    if 'volunteer_id' not in request.GET:
        if users.get_current_user():
            userID = users.get_current_user()
        else:
            return HttpResponseRedirect('/')
    else:
        userID = cgi.escape(request.GET['volunteer_id'])

        '''
        # marked by camge
        # Does google account must be xxxx@gmail.com ???
        if userID.find('@gmail.com') == -1:
            userID += '@gmail.com'
            userID = users.User(userID)
        '''

    user = flowBase.getVolunteer(userID)
    if not user:
        return HttpResponseRedirect('/')

    now = datetime.datetime.now()
    npoList = [NpoProfile.get(user.npo_profile_ref[i]) for i in range(displayNpoCount) if i < len(user.npo_profile_ref)]
    for npo in npoList:
        npo.eventList = npo.event2npo.fetch(displayNpoEventCount)
        for event in npo.eventList:
            event.diffDays = (event.start_time - now).days
            event.upcoming = True if event.diffDays >= 0 and event.diffDays <= diffDaysLimit else False
            
        npo.memberCount = len(npo.members)
        if npo.brief_intro:
            npo.brief_intro = npo.brief_intro if len(npo.brief_intro) < 15 else npo.brief_intro[0:15] + u'...'
    
    # page: home, added by tom_chen... nasty workaround
    template_values = {
            'base':                     flowBase.getBase(request, 'volunteer'),
            'volunteerBase':            flowBase.getVolunteerBase(user),
            'page':                     'npo',
            'npoList':                  npoList,
    }
    response = render_to_response('volunteer/joined_npo.html', template_values)

    return response

