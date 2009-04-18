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
displayNpoCount = 3
displayExpertiseCount = 5

def show(request):
    pageSet = paging.get(request.GET, VolunteerProfile.all().totalCount(), displayCount=displayCount)

    entryList = VolunteerProfile.all().order('-id').fetch(displayCount, pageSet['entryOffset'])
    for volunteer in entryList:
        volunteer.npoList = [NpoProfile.get(volunteer.npo_profile_ref[i]) for i in range(displayNpoCount) if i < len(volunteer.npo_profile_ref)]
        for npo in volunteer.npoList:
            if len(npo.npo_name) > 12:
                npo.npo_name = npo.npo_name[:12] + u'...'

        volunteer.npoCount = len(volunteer.npo_profile_ref)
        volunteer.npoShowMore = True if volunteer.npoCount > displayNpoCount else False
        volunteer.showExpertise = u', '.join(volunteer.expertise[:displayExpertiseCount])
        if (len(volunteer.expertise) > displayExpertiseCount):
            volunteer.showExpertise += u', ...'

    template_values = {
            'base':                     flowBase.getBase(request, 'volunteer'),
            'pageSet':                  pageSet,
            'entryList':                entryList,
            'firstEntry':               entryList[0] if len(entryList) > 0 else None,
    }
    response = render_to_response('volunteer/volunteer_list.html', template_values)

    return response

