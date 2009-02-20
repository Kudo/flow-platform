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
from db.ddl import NpoProfile, EventProfile

displayCount = 10
displayPageCount = 5
displayNpoEventCount = 2
diffDaysLimit = 14

def show(request):
    count = db.GqlQuery('SELECT * FROM NpoProfile').count()
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

    now = datetime.datetime.now()
    entryList = db.GqlQuery('SELECT * FROM NpoProfile ORDER BY id').fetch(displayCount, startIndex)
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
    }
    response = render_to_response('npo/npo_list.html', template_values)

    return response

