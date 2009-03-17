#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import feedDiscover
import feedparser
from django.utils import simplejson
from google.appengine.api import urlfetch
from django.http import HttpResponse

displayCount = 5
displayContentLength = 100

def get(request):
    feedUri = request.GET.get('feedUri', None)
    if not feedUri:
        return HttpResponse(simplejson.dumps({'statusCode': 404, 'reason': 'Unknown action'}), mimetype='application/json')
    feedList = feedDiscover.getFeedList(feedUri)
    host = re.match(r'(http://[^/?]+)', feedUri).group(1)
    if feedList:
        if re.match(r'http://', feedList[0]['uri']):
            feedUri = feedList[0]['uri']
        else:
            feedUri = '%s/%s' % (host, feedList[0]['uri'])
    try:
        fetchObj = urlfetch.fetch(feedUri)
        if fetchObj.status_code != 200:
            raise IOError
        parseObj = feedparser.parse(fetchObj.content)
    except:
        return HttpResponse(simplejson.dumps({'statusCode': 500, 'reason': 'Fail to parse feed'}), mimetype='application/json')
    entryList = []
    for entry in parseObj.entries[:displayCount]:
        summary = getattr(entry, 'summary', None)
        if not summary:
            summary = getattr(entry, 'content', None)
            if summary:
                summary = summary[0].value
        if summary:
            summary = summary[:displayContentLength]
        entryList.append({
            'title': entry.title, 
            'uri': entry.link, 
            'summary': summary,
        })
    return HttpResponse(simplejson.dumps({'statusCode': 200, 'reason': 'success', 'entryList': entryList}), mimetype='application/json')
