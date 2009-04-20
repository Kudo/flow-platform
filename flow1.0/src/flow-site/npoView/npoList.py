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
    pageSet = paging.get(request.GET, NpoProfile.all().totalCount(), displayCount=displayCount)

    now = datetime.datetime.now()
    entryList = NpoProfile.all().order('-id').fetch(displayCount, pageSet['entryOffset'])
    for npo in entryList:
        npo.eventList = npo.event2npo.fetch(displayNpoEventCount)
        for event in npo.eventList:
            event.event_name = event.event_name if len(event.event_name) < 15 else event.event_name[:15] + u'...'
            event.diffDays = (event.start_time - now).days
            event.upcoming = True if event.diffDays >= 0 and event.diffDays <= diffDaysLimit else False

        npo.memberCount = len(npo.members)
        npo.region = u', '.join(npo.service_region)
        npo.region = npo.region if len(npo.region) < 15 else npo.region[0:15] + u'...'
        if npo.brief_intro:
            npo.brief_intro = npo.brief_intro if len(npo.brief_intro) < 50 else npo.brief_intro[:50] + u'...'

    template_values = {
            'base':                     flowBase.getBase(request, 'npo'),
            'pageSet':                  pageSet,
            'entryList':                entryList,
            'firstEntry':               entryList[0] if len(entryList) > 0 else None,
    }
    response = render_to_response('npo/npo_list.html', template_values)

    return response

