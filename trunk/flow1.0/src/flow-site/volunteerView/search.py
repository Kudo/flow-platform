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
    searchVal['searchExpertise_1'] = request.GET.get('expertise_1') and request.GET.get('expertise_1').decode('UTF-8')
    searchVal['searchExpertise_2'] = request.GET.get('expertise_2') and request.GET.get('expertise_2').decode('UTF-8')
    searchVal['searchExpertise_3'] = request.GET.get('expertise_3') and request.GET.get('expertise_3').decode('UTF-8')

    queryStringList = []
    searchExpertiseList = set()
    if searchVal['searchExpertise_1']:
        searchExpertiseList.add(searchVal['searchExpertise_1'])
        queryStringList.append(u'expertise_1=%s' % searchVal['searchExpertise_1'])
    if searchVal['searchExpertise_2']:
        searchExpertiseList.add(searchVal['searchExpertise_2'])
        queryStringList.append(u'expertise_2=%s' % searchVal['searchExpertise_2'])
    if searchVal['searchExpertise_3']:
        searchExpertiseList.add(searchVal['searchExpertise_3'])
        queryStringList.append(u'expertise_3=%s' % searchVal['searchExpertise_3'])

    queryObj = VolunteerProfile.all()
    if searchVal['searchRegion']:
        queryObj.filter('resident_city = ', searchVal['searchRegion'])
        queryStringList.append(u'region=%s' % searchVal['searchRegion'])
    if len(searchExpertiseList) > 0:
        queryObj.filter('expertise in ', list(searchExpertiseList))
    del searchExpertiseList

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
    }
    response = render_to_response('volunteer/volunteer_search.html', template_values)

    return response

