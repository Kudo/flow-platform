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

def show(request):
    searchVal = {}
    searchVal['searchRegion'] = request.GET.get('region') and request.GET.get('region').decode('UTF-8')
    searchVal['searchExpertise_1'] = request.GET.get('expertise_1') and request.GET.get('expertise_1').decode('UTF-8')
    searchVal['searchExpertise_2'] = request.GET.get('expertise_2') and request.GET.get('expertise_2').decode('UTF-8')
    searchVal['searchExpertise_3'] = request.GET.get('expertise_3') and request.GET.get('expertise_3').decode('UTF-8')

    searchExpertiseList = set()
    if searchVal['searchExpertise_1']:
        searchExpertiseList.add(searchVal['searchExpertise_1'])
    if searchVal['searchExpertise_2']:
        searchExpertiseList.add(searchVal['searchExpertise_2'])
    if searchVal['searchExpertise_3']:
        searchExpertiseList.add(searchVal['searchExpertise_3'])

    queryObj = VolunteerProfile.all()
    if searchVal['searchRegion']:
        queryObj.filter('resident_city = ', searchVal['searchRegion'])
    if len(searchExpertiseList) > 0:
        queryObj.filter('expertise in ', list(searchExpertiseList))

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
            'searchVal':                searchVal,
    }
    response = render_to_response('volunteer/volunteer_search.html', template_values)

    return response

