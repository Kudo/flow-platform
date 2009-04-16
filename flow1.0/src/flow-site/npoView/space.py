#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import cgi
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.utils import simplejson
from google.appengine.ext import db
from google.appengine.api import users
import flowBase
from common import paging
from db.ddl import NpoProfile

displayCount = 10
displayPageCount = 5
displayPhotoCount = 5

def show(request, npoid, displayAlbumCount=2, displayArticleCount=5):
    target = flowBase.getNpo(npo_id=npoid)
    if not target:
        return HttpResponseRedirect('/')

    from datetime import datetime
    import atom.url
    import gdata.alt.appengine
    import gdata.photos.service
    import gdata.youtube.service

    # Picasa Web
    albums = []
    service = gdata.photos.service.PhotosService()
    gdata.alt.appengine.run_on_appengine(service)
    for albumLink in target.photo_link[:displayAlbumCount]:
        try:
            album = service.GetEntry('http://picasaweb.google.com/data/entry/api/user/%s' % albumLink)
            albums.append({'albumFeed': album, 'photoFeeds': service.GetFeed(album.GetPhotosUri(), limit=displayPhotoCount).entry}) 
        except:
            pass

    # Youtube
    video = None
    videoDate = None
    service = gdata.youtube.service.YouTubeService()
    gdata.alt.appengine.run_on_appengine(service)
    for vid in target.video_link:
        try:
            video = service.GetYouTubeVideoEntry(video_id=vid)
            videoDate = datetime.strptime(video.published.text, '%Y-%m-%dT%H:%M:%S.000Z')
        except:
            continue
        break

    template_values = {
            'isAdmin':                  True if flowBase.isNpoAdmin(npo=target) else False,
            'npoProfile':               target,
            'base':                     flowBase.getBase(request, 'npo'),
            'page':                     'space',
            'albums':                   albums,
            'video':                    video,
            'videoDate':                videoDate,
            'videoCount':               len(target.video_link),
            'albumUri':                 target.saved_picasa_link or '',
            'feedUri':                  target.saved_feed_link or '',
            'articleList':              [obj.rsplit(u',http://', 1) for obj in target.article_link][:displayArticleCount],
            'articleCount':             len(target.article_link),
    }
    response = render_to_response('npo/npo_space.html', template_values)

    return response

def albumShow(request, npoid, displayCount=5):
    target = flowBase.getNpo(npo_id=npoid)
    if not target:
        return HttpResponseRedirect('/')

    pageSet = paging.get(request.GET, len(target.photo_link), displayCount=displayCount)

    from datetime import datetime
    import atom.url
    import gdata.alt.appengine
    import gdata.photos.service
    service = gdata.photos.service.PhotosService()
    gdata.alt.appengine.run_on_appengine(service)

    albumLinkList = target.photo_link[pageSet['entryOffset']:pageSet['entryOffset'] + displayCount]
    entryList = []
    for albumLink in albumLinkList:
        try:
            album = service.GetEntry('http://picasaweb.google.com/data/entry/api/user/%s' % albumLink)
            albumEntry = {'albumFeed': album, 'photoFeeds': service.GetFeed(album.GetPhotosUri(), limit=displayPhotoCount).entry}
        except:
            albumEntry = None
        entryList.append(albumEntry)

    template_values = {
            'isAdmin':                  True if flowBase.isNpoAdmin(npo=target) else False,
            'npoProfile':               target,
            'base':                     flowBase.getBase(request, 'npo'),
            'entryList':                entryList,
            'albumUri':                 target.saved_picasa_link or '',
            'page':                     'space',
            'pageSet':                  pageSet,
    }

    return render_to_response('npo/album_list.html', template_values)

def albumCreate(request, npoid):
    import re

    target = flowBase.getNpo(npo_id=npoid)
    isNpoAdmin = flowBase.isNpoAdmin(npo=target)
    if not target or not isNpoAdmin:
        return HttpResponse(simplejson.dumps({'statusCode': 403, 'reason': 'No login'}), mimetype='application/json')

    itemList = request.POST.getlist('itemList')
    try:
        for albumUri in itemList:
            if re.match(r'(\w+)/albumid/(.+)$', albumUri):
                target.photo_link.insert(0, albumUri)
        target.put()
    except:
        return HttpResponse(simplejson.dumps({'statusCode': 500, 'reason': str(sys.exc_info())}), mimetype='application/json')
    return HttpResponse(simplejson.dumps({'statusCode': 200, 'reason': 'success'}), mimetype='application/json')

def albumDelete(request, npoid):
    target = flowBase.getNpo(npo_id=npoid)
    isNpoAdmin = flowBase.isNpoAdmin(npo=target)
    if not target or not isNpoAdmin:
        return HttpResponse(simplejson.dumps({'statusCode': 403, 'reason': 'No login'}), mimetype='application/json')

    itemId = int(request.GET.get('itemId', 0))
    if itemId >= 0:
        try:
            target.photo_link.pop(itemId - 1)
            target.put()
        except:
            return HttpResponse(simplejson.dumps({'statusCode': 500, 'reason': str(sys.exc_info())}), mimetype='application/json')
        return HttpResponse(simplejson.dumps({'statusCode': 200, 'reason': 'success'}), mimetype='application/json')
    else:
        return HttpResponse(simplejson.dumps({'statusCode': 501, 'reason': 'Unknown action'}), mimetype='application/json')


def videoShow(request, npoid, displayCount=5):
    target = flowBase.getNpo(npo_id=npoid)
    if not target:
        return HttpResponseRedirect('/')

    pageSet = paging.get(request.GET, len(target.video_link), displayCount=displayCount)

    from datetime import datetime
    import atom.url
    import gdata.alt.appengine
    import gdata.youtube.service
    service = gdata.youtube.service.YouTubeService()
    gdata.alt.appengine.run_on_appengine(service)

    vidList = target.video_link[pageSet['entryOffset']:pageSet['entryOffset'] + displayCount]
    entryList = []
    for vid in vidList:
        try:
            video = service.GetYouTubeVideoEntry(video_id=vid)
            videoDate = datetime.strptime(video.published.text, '%Y-%m-%dT%H:%M:%S.000Z')
            video.videoDate = videoDate
        except:
            video = None
        entryList.append(video)

    template_values = {
            'isAdmin':                  True if flowBase.isNpoAdmin(npo=target) else False,
            'npoProfile':               target,
            'base':                     flowBase.getBase(request, 'npo'),
            'entryList':                entryList,
            'firstEntry':               entryList[0] if len(entryList) > 0 else None,
            'page':                     'space',
            'pageSet':                  pageSet,
    }

    return render_to_response('npo/video_list.html', template_values)

def videoCreate(request, npoid):
    import re
    target = flowBase.getNpo(npo_id=npoid)
    isNpoAdmin = flowBase.isNpoAdmin(npo=target)
    if not target or not isNpoAdmin:
        return HttpResponse(simplejson.dumps({'statusCode': 403, 'reason': 'No login'}), mimetype='application/json')

    youtubeUri = request.POST.get('videoUri', None)
    try:
        matchObj = re.match(r'http://\w+\.youtube\.com(\.tw)?/.*[&?]v=(.+?)(&.*)*$', youtubeUri)
        if matchObj:
            uri = matchObj.group(2)
            target.video_link.insert(0, uri)
            target.put()
    except:
        return HttpResponse(simplejson.dumps({'statusCode': 500, 'reason': str(sys.exc_info())}), mimetype='application/json')
    return HttpResponse(simplejson.dumps({'statusCode': 200, 'reason': 'success'}), mimetype='application/json')

def videoDelete(request, npoid):
    target = flowBase.getNpo(npo_id=npoid)
    isNpoAdmin = flowBase.isNpoAdmin(npo=target)
    if not target or not isNpoAdmin:
        return HttpResponse(simplejson.dumps({'statusCode': 403, 'reason': 'No login'}), mimetype='application/json')

    itemId = int(request.GET.get('itemId', 0))
    if itemId >= 0:
        try:
            target.video_link.pop(itemId - 1)
            target.put()
        except:
            return HttpResponse(simplejson.dumps({'statusCode': 500, 'reason': str(sys.exc_info())}), mimetype='application/json')
        return HttpResponse(simplejson.dumps({'statusCode': 200, 'reason': 'success'}), mimetype='application/json')
    else:
        return HttpResponse(simplejson.dumps({'statusCode': 501, 'reason': 'Unknown action'}), mimetype='application/json')

def articleShow(request, npoid):
    target = flowBase.getNpo(npo_id=npoid)
    if not target:
        return HttpResponseRedirect('/')

    pageSet = paging.get(request.GET, len(target.article_link), displayCount=displayCount)
    entryList = [obj.rsplit(u',http://', 1) for obj in target.article_link[pageSet['entryOffset']:pageSet['entryOffset'] + displayCount]]

    template_values = {
            'isAdmin':                  True if flowBase.isNpoAdmin(npo=target) else False,
            'base':                     flowBase.getBase(request, 'npo'),
            'entryList':                entryList,
            'firstEntry':               entryList[0] if len(entryList) > 0 else None,
            'feedUri':                  target.saved_feed_link or '',
            'page':                     'space',
            'pageSet':                  pageSet,
    }

    return render_to_response('npo/article_list.html', template_values)

def articleCreate(request, npoid):
    import re
    target = flowBase.getNpo(npo_id=npoid)
    isNpoAdmin = flowBase.isNpoAdmin(npo=target)
    if not target or not isNpoAdmin:
        return HttpResponse(simplejson.dumps({'statusCode': 403, 'reason': 'No login'}), mimetype='application/json')

    itemList = request.POST.getlist('itemList')
    try:
        for item in itemList:
            # Ref: http://regexlib.com/RETester.aspx?regexp_id=96
            if re.match('^.+,(http://){2}[\w\-_]+(\.[\w\-_]+)+([\w\-\.,@?^=%&amp;:/~\+#]*[\w\-\@?^=%&amp;/~\+#])?$', item):
                target.article_link.insert(0, item.decode('UTF-8'))
        target.put()
    except:
        return HttpResponse(simplejson.dumps({'statusCode': 500, 'reason': str(sys.exc_info())}), mimetype='application/json')
    return HttpResponse(simplejson.dumps({'statusCode': 200, 'reason': 'success'}), mimetype='application/json')

def articleDelete(request, npoid):
    target = flowBase.getNpo(npo_id=npoid)
    isNpoAdmin = flowBase.isNpoAdmin(npo=target)
    if not target or not isNpoAdmin:
        return HttpResponse(simplejson.dumps({'statusCode': 403, 'reason': 'No login'}), mimetype='application/json')

    itemId = int(request.GET.get('itemId', 0))
    if itemId >= 0:
        try:
            target.article_link.pop(itemId - 1)
            target.put()
        except:
            return HttpResponse(simplejson.dumps({'statusCode': 500, 'reason': str(sys.exc_info())}), mimetype='application/json')
        return HttpResponse(simplejson.dumps({'statusCode': 200, 'reason': 'success'}), mimetype='application/json')
    else:
        return HttpResponse(simplejson.dumps({'statusCode': 501, 'reason': 'Unknown action'}), mimetype='application/json')

def albumUriSave(request, npoid):
    import re
    target = flowBase.getNpo(npo_id=npoid)
    isNpoAdmin = flowBase.isNpoAdmin(npo=target)
    if not target or not isNpoAdmin:
        return HttpResponse(simplejson.dumps({'statusCode': 403, 'reason': 'No login'}), mimetype='application/json')

    albumUri = request.POST.get('albumUri', None)
    if albumUri:
        try:
            matchObj = re.match(r'(http://picasaweb\.google\.com(\.tw)?/\w+?(/|$))', albumUri)
            if matchObj:
                target.saved_picasa_link = matchObj.group(1)
                target.put()
        except:
            return HttpResponse(simplejson.dumps({'statusCode': 500, 'reason': str(sys.exc_info())}), mimetype='application/json')
        return HttpResponse(simplejson.dumps({'statusCode': 200, 'reason': 'success'}), mimetype='application/json')
    else:
        return HttpResponse(simplejson.dumps({'statusCode': 501, 'reason': 'Unknown action'}), mimetype='application/json')

def feedUriSave(request, npoid):
    target = flowBase.getNpo(npo_id=npoid)
    isNpoAdmin = flowBase.isNpoAdmin(npo=target)
    if not target or not isNpoAdmin:
        return HttpResponse(simplejson.dumps({'statusCode': 403, 'reason': 'No login'}), mimetype='application/json')

    feedUri = request.POST.get('feedUri', None)
    if feedUri:
        try:
            target.saved_feed_link = feedUri
            target.put()
        except:
            return HttpResponse(simplejson.dumps({'statusCode': 500, 'reason': str(sys.exc_info())}), mimetype='application/json')
        return HttpResponse(simplejson.dumps({'statusCode': 200, 'reason': 'success'}), mimetype='application/json')
    else:
        return HttpResponse(simplejson.dumps({'statusCode': 501, 'reason': 'Unknown action'}), mimetype='application/json')
