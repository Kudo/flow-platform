#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import cgi
import datetime
from django.shortcuts import render_to_response
import flowBase
from common import paging
from db.ddl import EventProfile

displayCount = 10

def show(request):
    searchVal = {}
    searchVal['searchTags'] = request.GET.get('tags') and request.GET.get('tags').decode('UTF-8')
    searchVal['searchRegion'] = request.GET.get('region') and request.GET.get('region').decode('UTF-8')

    queryStringList = []
    queryObj = EventProfile.all()
    displayStr = u''

    if searchVal['searchTags']:
        queryObj.filter('tag in ', [s.strip() for s in searchVal['searchTags'].split(',')])
        queryStringList.append(u'tags=%s' % searchVal['searchTags'])
        displayStr += u'與 <span class="highlight">' + searchVal['searchTags'] + '</span> 相關'
        if searchVal['searchRegion']:
            displayStr += u', 且'

    if searchVal['searchRegion']:
        queryObj.filter('event_region in ', [searchVal['searchRegion']])
        queryStringList.append(u'region=%s' % searchVal['searchRegion'])
        displayStr += u'地區為 <span class="highlight">' + searchVal['searchRegion'] + '</span> '

    pageSet = paging.get(request.GET, queryObj.count(), displayCount=displayCount)

    now = datetime.datetime.now()
    entryList = queryObj.order('-create_time').fetch(displayCount, pageSet['entryOffset'])
    for event in entryList:
        event.startTime = event.start_time.strftime('%Y-%m-%d %H:%M')
        event.region = u','.join(event.event_region)

    template_values = {
            'base':                     flowBase.getBase(request, 'event'),
            'pageSet':                  pageSet,
            'entryList':                entryList,
            'searchVal':                searchVal,
            'queryString':              u'&'.join(queryStringList),
            'displayStr':               displayStr,
    }
    response = render_to_response('event/event-search.html', template_values)

    return response

