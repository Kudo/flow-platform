#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import re
from django.utils import simplejson
from django.http import HttpResponse
import atom.url
import gdata.alt.appengine
import gdata.photos.service

displayAlbumCount = 5
displayPhotoCount = 5

def get(request):
    albumUri = request.POST.get('uri', None)
    if not albumUri:
        return HttpResponse(simplejson.dumps({'statusCode': 501, 'reason': 'Unknown action'}), mimetype='application/json; charset=utf-8')
    matchObj = re.match(r'(http://picasaweb\.google\.com(\.tw)?/(\w+?)(/|$))', albumUri)
    if not matchObj:
        return HttpResponse(simplejson.dumps({'statusCode': 500, 'reason': 'Fail to parse uri'}), mimetype='application/json; charset=utf-8')
    service = gdata.photos.service.PhotosService()
    gdata.alt.appengine.run_on_appengine(service)
    albums = []
    try:
        albumFeeds = service.GetUserFeed(user=matchObj.group(3), limit=displayAlbumCount).entry
        for album in albumFeeds:
            albums.append({
                'title':        album.title.text,
                'savedUri':     album.link[2].href[48:],
                'albumUri':     album.link[1].href,
                'thumbnail':    album.media.thumbnail[0].url,
                'albumDate':    album.timestamp.datetime().strftime('%Y.%m.%d'),
                'numphotos':    album.numphotos.text,
                'photos':       [(photo.link[1].href, photo.media.thumbnail[0].url) for photo in service.GetFeed(album.GetPhotosUri(), limit=displayPhotoCount).entry],
            })
        del albumFeeds
    except:
        return HttpResponse(simplejson.dumps({'statusCode': 500, 'reason': 'Fail to parse uri'}), mimetype='application/json; charset=utf-8')

    return HttpResponse(simplejson.dumps({'statusCode': 200, 'reason': 'success', 'entryList': albums}, ensure_ascii=False), mimetype='application/json; charset=utf-8')
