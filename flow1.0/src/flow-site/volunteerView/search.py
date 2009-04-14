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
    searchVal = {}
    searchVal['searchRegion'] = request.GET.get('region') and request.GET.get('region').decode('UTF-8')
    searchVal['searchExpertise'] = request.GET.get('expertise') and request.GET.get('expertise').decode('UTF-8')

    queryStringList = []
    queryObj = VolunteerProfile.all()
    displayStr = u''

    if searchVal['searchRegion']:
        queryObj.filter('resident_city = ', searchVal['searchRegion'])
        queryStringList.append(u'region=%s' % searchVal['searchRegion'])
        displayStr += u'居住地為 <span class="highlight">' + searchVal['searchRegion'] + '</span>'
        if searchVal['searchExpertise']:
            displayStr += u', 且'
        else:
            displayStr += u' '

    if searchVal['searchExpertise']:
        queryObj.filter('expertise = ', searchVal['searchExpertise'])
        queryStringList.append(u'expertise=%s' % searchVal['searchExpertise'])
        displayStr += u'專長為 <span class="highlight">' + searchVal['searchExpertise'] + '</span> '

    pageSet = paging.get(request.GET, queryObj.count(), displayCount=displayCount)

    entryList = queryObj.order('id').fetch(displayCount, pageSet['entryOffset'])
    for volunteer in entryList:
        volunteer.npoList = [NpoProfile.get(volunteer.npo_profile_ref[i]) for i in range(displayNpoCount) if i < len(volunteer.npo_profile_ref)]
        volunteer.npoCount = len(volunteer.npo_profile_ref)
        volunteer.npoShowMore = True if volunteer.npoCount > displayNpoCount else False
        volunteer.showExpertise = u', '.join(volunteer.expertise[:displayExpertiseCount])

    template_values = {
            'base':                     flowBase.getBase(request, 'volunteer'),
            'pageSet':                  pageSet,
            'entryList':                entryList,
            'firstEntry':               entryList[0] if len(entryList) > 0 else None,
            'searchVal':                searchVal,
            'queryString':              u'&'.join(queryStringList),
            'displayStr':               displayStr,
    }
    response = render_to_response('volunteer/volunteer_search.html', template_values)

    return response

