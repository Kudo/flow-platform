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

def show(request, npoid, displayAlbumCount=2, displayPhotoCount=5, displayArticleCount=5):
    target = flowBase.getNpo(npo_id=npoid)
    if not target:
        return HttpResponseRedirect('/')

    from datetime import datetime
    import atom.url
    import gdata.alt.appengine
    import gdata.photos, gdata.photos.service
    import gdata.photos, gdata.youtube.service

    # Picasa Web
    picasaUser = 'ckchien'
    service = gdata.photos.service.PhotosService()
    gdata.alt.appengine.run_on_appengine(service)
    try:
        albumFeeds = service.GetUserFeed(user=picasaUser, limit=displayAlbumCount).entry
        albums = [{'albumFeed': album, 'photoFeeds': service.GetEntry(album.GetPhotosUri(), limit=displayPhotoCount)} for album in albumFeeds] 
    except:
        albumFeeds = None
        albums = None
    #return HttpResponse(albums[0]['photoFeeds'][0], mimetype="text/xml")
    #photos = service.SearchUserPhotos(query='若水', user='ckchien').entry
    del albumFeeds

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
            'articleList':              [obj.rsplit(u',http://', 1) for obj in target.article_link][:displayArticleCount],
            'articleCount':             len(target.article_link),
    }
    response = render_to_response('npo/npo_space.html', template_values)

    return response

def videoShow(request, npoid, displayCount=5):
    target = flowBase.getNpo(npo_id=npoid)
    if not target:
        return HttpResponseRedirect('/')

    pageSet = paging.get(request.GET, len(target.video_link), displayCount=displayCount)

    from datetime import datetime
    import atom.url
    import gdata.alt.appengine
    import gdata.photos, gdata.youtube.service
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
        return HttpResponse(simplejson.dumps({'statusCode': 501, 'reason': 'No login'}), mimetype='application/json')

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
        return HttpResponse(simplejson.dumps({'statusCode': 501, 'reason': 'No login'}), mimetype='application/json')

    itemId = int(request.GET.get('itemId', 0))
    if itemId >= 0:
        try:
            target.video_link.pop(itemId - 1)
            target.put()
        except:
            return HttpResponse(simplejson.dumps({'statusCode': 500, 'reason': str(sys.exc_info())}), mimetype='application/json')
        return HttpResponse(simplejson.dumps({'statusCode': 200, 'reason': 'success'}), mimetype='application/json')
    else:
        return HttpResponse(simplejson.dumps({'statusCode': 404, 'reason': 'Unknown action'}), mimetype='application/json')

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
        return HttpResponse(simplejson.dumps({'statusCode': 501, 'reason': 'No login'}), mimetype='application/json')

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
        return HttpResponse(simplejson.dumps({'statusCode': 501, 'reason': 'No login'}), mimetype='application/json')

    itemId = int(request.GET.get('itemId', 0))
    if itemId >= 0:
        try:
            target.article_link.pop(itemId - 1)
            target.put()
        except:
            return HttpResponse(simplejson.dumps({'statusCode': 500, 'reason': str(sys.exc_info())}), mimetype='application/json')
        return HttpResponse(simplejson.dumps({'statusCode': 200, 'reason': 'success'}), mimetype='application/json')
    else:
        return HttpResponse(simplejson.dumps({'statusCode': 404, 'reason': 'Unknown action'}), mimetype='application/json')

def feedUriSave(request, npoid):
    target = flowBase.getNpo(npo_id=npoid)
    isNpoAdmin = flowBase.isNpoAdmin(npo=target)
    if not target or not isNpoAdmin:
        return HttpResponse(simplejson.dumps({'statusCode': 501, 'reason': 'No login'}), mimetype='application/json')

    feedUri = request.POST.get('feedUri', None)
    if feedUri:
        try:
            target.saved_feed_link = feedUri
            target.put()
        except:
            return HttpResponse(simplejson.dumps({'statusCode': 500, 'reason': str(sys.exc_info())}), mimetype='application/json')
        return HttpResponse(simplejson.dumps({'statusCode': 200, 'reason': 'success'}), mimetype='application/json')
    else:
        return HttpResponse(simplejson.dumps({'statusCode': 404, 'reason': 'Unknown action'}), mimetype='application/json')
