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
from db.ddl import VolunteerProfile, VolunteerIm, NpoProfile

displayCount = 10
displayNpoCount = 3
displayPageCount = 5

def list(request):
    searchRegion = request.GET.get('region', default='any').decode('UTF-8')
    searchExpertise = request.GET.get('expertise', default='any').decode('UTF-8')

    queryObj = VolunteerProfile.all()
    if searchRegion != 'any':
        queryObj.filter('resident_city = ', searchRegion)
    if searchExpertise != 'any':
        queryObj.filter('expertise = ', searchExpertise)

    count = queryObj.count()

    startIndex = 0
    if 'start' in request.GET:
        startIndex = int(request.GET['start'])
        if startIndex < 0 or startIndex >= count:
            startIndex = 0
    endIndex = startIndex + displayCount - 1
    if endIndex >= count:
        endIndex = count - 1

    currentPage = startIndex / displayCount + 1
    totalPage = (count - 1) / displayCount + 1

    # Calculate the page list window
    if totalPage < 1:
        totalPage = 1
    fromPage = currentPage -  (displayPageCount / 2)
    if fromPage < 1:
        fromPage = 1
    endPage = fromPage + displayPageCount
    while endPage > totalPage + 1:
        fromPage -= 1
        endPage -= 1
    if fromPage < 1:
        fromPage = 1
    pageList = [{'index': i, 'startIndex': (i - 1) * displayCount} for i in range(fromPage, endPage)]
    del fromPage, endPage

    entryList = queryObj.order('id').fetch(displayCount, startIndex)
    for volunteer in entryList:
        volunteer.npoList = [NpoProfile.get(volunteer.npo_profile_ref[i]) for i in range(displayNpoCount) if i < len(volunteer.npo_profile_ref)]
        volunteer.npoCount = len(volunteer.npo_profile_ref)
        volunteer.npoShowMore = True if volunteer.npoCount > displayNpoCount else False
        volunteer.showExpertise = u', '.join(volunteer.expertise)

    # Special case, if count <= 0
    if count <= 0:
        startIndex = -1

    template_values = {
            'base':                     flowBase.getBase(request),
            'count':                    count,
            'startIndex':               startIndex,
            'nextIndex':                startIndex + displayCount if currentPage < totalPage else None,
            'prevIndex':                startIndex - displayCount if currentPage > 1 else None,
            'endIndex':                 endIndex,
            'entryList':                entryList,
            'firstEntry':               entryList[0] if len(entryList) > 0 else None,
            'pageList':                 pageList,
            'currentPage':              currentPage,
            'searchVal':                {'region': searchRegion, 'expertise': searchExpertise},
    }
    response = render_to_response('volunteer/volunteer_search.html', template_values)

    return response
