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
from db.ddl import NpoProfile, EventProfile

displayCount = 10
displayNpoEventCount = 2
diffDaysLimit = 14

def show(request):
    searchVal = {}
    searchVal['searchRegion'] = request.GET.get('region') and request.GET.get('region').decode('UTF-8')

    queryStringList = []
    queryObj = NpoProfile.all()
    if searchVal['searchRegion']:
        queryObj.filter('service_region in ', [searchVal['searchRegion']])
        queryStringList.append(u'region=%s' % searchVal['searchRegion'])

    pageSet = paging.get(request.GET, queryObj.count(), displayCount=displayCount)

    now = datetime.datetime.now()
    entryList = queryObj.order('id').fetch(displayCount, pageSet['entryOffset'])
    for npo in entryList:
        npo.eventList = npo.event2npo.fetch(displayNpoEventCount)
        for event in npo.eventList:
            event.diffDays = (event.start_time - now).days
            event.upcoming = True if event.diffDays >= 0 and event.diffDays <= diffDaysLimit else False

        npo.memberCount = len(npo.members)
        npo.region = u', '.join(npo.service_region)
        npo.region = npo.region if len(npo.region) < 15 else npo.region[0:15] + u'...'
        if npo.brief_intro:
            npo.brief_intro = npo.brief_intro if len(npo.brief_intro) < 15 else npo.brief_intro[0:15] + u'...'

    template_values = {
            'base':                     flowBase.getBase(request),
            'pageSet':                  pageSet,
            'entryList':                entryList,
            'firstEntry':               entryList[0] if len(entryList) > 0 else None,
            'searchVal':                searchVal,
            'queryString':              u'&'.join(queryStringList),
    }
    response = render_to_response('npo/npo_search.html', template_values)

    return response

