#!/usr/bin/env python
"""A simple feed discovery program

Given a url, try to discover all the feeds, and return {'type': 'rss or atom or unknown', 'uri': 'someUri', 'title': 'feedTtitle'} in list.

Currently support type is rss and atom.

"""
import re
from google.appengine.api import urlfetch
from sgmllib import SGMLParser

# Ref from: http://diveintomark.org/archives/2002/05/31/rss_autodiscovery_in_python
class LinkParser(SGMLParser):
    feedList = []
    def reset(self):
        SGMLParser.reset(self)
        self.feedList = []

    def do_link(self, attrs):
        if not ('rel', 'alternate') in attrs: return
        isRSS = True if ('type', 'application/rss+xml') in attrs else False
        isAtom = True if ('type', 'application/atom+xml') in attrs else False
        uri = None
        title = None
        for attr in attrs:
            if attr[0] == 'href':
                uri = attr[1]
            if attr[0] == 'title':
                title = attr[1]
        if isAtom:
            self.feedList.append({'type': 'atom', 'uri': uri, 'title': title})
        elif isRSS:
            self.feedList.append({'type': 'rss', 'uri': uri, 'title': title})
        else:
            return

    def end_head(self, attrs):
        self.setnomoretags()
    start_body = end_head

def isFeed(content):
    """
    Currrently just check if is is xml or not
    """
    if re.match(r'<\?xml.+?\?>', content):
        return True
    return False

def getFeedList(uri):
    try:
        fetchObj = urlfetch.fetch(uri, allow_truncated=True)
    except:
        return []
    if fetchObj.status_code != 200:
        return []
    content = fetchObj.content.lower()
    del fetchObj

    if isFeed(content):
        return [{'type': 'unknown', 'uri': uri, 'title': None}]

    feedList = []
    linkParserObj = LinkParser()
    linkParserObj.feed(content)
    if not linkParserObj.nomoretags:
        return feedList
    for feed in linkParserObj.feedList:
        feedList.append(feed)
    return feedList

def unitTest(request):
    from django.http import HttpResponse
    response = HttpResponse(mimetype="text/plain; charset=utf-8")
    uris = [
            'http://www.kudo.idv.tw/blog/', 
            'http://kudo.csie.info/', 
            'http://www.cs.ccu.edu.tw/', 
            'http://non-existent/', 
            'http://feeds.feedburner.com/Kudo',
    ]
    for uri in uris:
        response.write(str(getFeedList(uri)) + '\n')
    return response
