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
from db.ddl import VolunteerProfile, VolunteerIm

displayCount = 10
displayPageCount = 5

def show(request, displayAlbumCount=2, displayPhotoCount=5, displayArticleCount=5):
    user = flowBase.verifyVolunteer(request)
    if not user:
        return HttpResponseRedirect('/')

    base = flowBase.getBase(request, 'volunteer')

    from datetime import datetime
    import atom.url
    import gdata.alt.appengine
    import gdata.photos, gdata.photos.service
    import gdata.photos, gdata.youtube.service

    # Picasa Web
    picasaUser = 'ckchien'
    service = gdata.photos.service.PhotosService()
    gdata.alt.appengine.run_on_appengine(service)
    albumFeeds = service.GetUserFeed(user=picasaUser, limit=displayAlbumCount).entry
    albums = [{'albumFeed': album, 'photoFeeds': service.GetEntry(album.GetPhotosUri(), limit=displayPhotoCount)} for album in albumFeeds] 
    #return HttpResponse(albums[0]['photoFeeds'][0], mimetype="text/xml")
    #photos = service.SearchUserPhotos(query='若水', user='ckchien').entry
    del albumFeeds

    # Youtube
    video = None
    videoDate = None
    if len(user.video_link) > 0:
        vid = user.video_link[0]
        service = gdata.youtube.service.YouTubeService()
        gdata.alt.appengine.run_on_appengine(service)
        video = service.GetYouTubeVideoEntry(video_id=vid)
        videoDate = datetime.strptime(video.published.text, '%Y-%m-%dT%H:%M:%S.000Z')

    template_values = {
            'isSelf':                   True if base['user'] == user.volunteer_id else False,
            'base':                     base,
            'volunteerBase':            flowBase.getVolunteerBase(user),
            'page':                     'space',
            'albums':                   albums,
            'video':                    video,
            'videoDate':                videoDate,
            'articleList':              [obj.rsplit(u',http://', 1) for obj in user.article_link][:displayArticleCount],
    }
    response = render_to_response('volunteer/profile_space.html', template_values)

    return response

def videoShow(request, displayCount=5):
    user = flowBase.verifyVolunteer(request)
    if not user:
        return HttpResponseRedirect('/')

    base = flowBase.getBase(request, 'volunteer')
    pageSet = paging.get(request.GET, len(user.video_link), displayCount=displayCount)

    from datetime import datetime
    import atom.url
    import gdata.alt.appengine
    import gdata.photos, gdata.youtube.service
    service = gdata.youtube.service.YouTubeService()
    gdata.alt.appengine.run_on_appengine(service)

    vidList = user.video_link[pageSet['entryOffset']:pageSet['entryOffset'] + displayCount]
    entryList = []
    for vid in vidList:
        video = service.GetYouTubeVideoEntry(video_id=vid)
        videoDate = datetime.strptime(video.published.text, '%Y-%m-%dT%H:%M:%S.000Z')
        video.videoDate = videoDate
        entryList.append(video)

    template_values = {
            'isSelf':                   True if base['user'] == user.volunteer_id else False,
            'base':                     base,
            'volunteerBase':            flowBase.getVolunteerBase(user),
            'entryList':                entryList,
            'firstEntry':               entryList[0] if len(entryList) > 0 else None,
            'page':                     'space',
            'pageSet':                  pageSet,
            'queryString':              'volunteer_id=%s' % (user.volunteer_id.email()),
    }

    return render_to_response('volunteer/video_list.html', template_values)

def videoCreate(request):
    import re
    user = flowBase.getVolunteer(users.get_current_user())
    if not user:
        return HttpResponse(simplejson.dumps({'statusCode': 501, 'reason': 'No login'}), mimetype='application/json')
    youtubeUri = request.POST.get('videoUri', None)
    try:
        matchObj = re.match(r'http://\w+\.youtube\.com(\.tw)?/.*[&?]v=(.+?)(&.*)*$', youtubeUri)
        if matchObj:
            uri = matchObj.group(2)
            user.video_link.insert(0, uri)
            user.put()
    except:
        return HttpResponse(simplejson.dumps({'statusCode': 500, 'reason': str(sys.exc_info())}), mimetype='application/json')
    return HttpResponse(simplejson.dumps({'statusCode': 200, 'reason': 'success'}), mimetype='application/json')

def videoDelete(request):
    user = flowBase.getVolunteer(users.get_current_user())
    if not user:
        return HttpResponse(simplejson.dumps({'statusCode': 501, 'reason': 'No login'}), mimetype='application/json')
    itemId = int(request.GET.get('itemId', 0))
    if itemId >= 0:
        try:
            user.video_link.pop(itemId - 1)
            user.put()
        except:
            return HttpResponse(simplejson.dumps({'statusCode': 500, 'reason': str(sys.exc_info())}), mimetype='application/json')
        return HttpResponse(simplejson.dumps({'statusCode': 200, 'reason': 'success'}), mimetype='application/json')
    else:
        return HttpResponse(simplejson.dumps({'statusCode': 404, 'reason': 'Unknown action'}), mimetype='application/json')

def articleShow(request):
    user = flowBase.verifyVolunteer(request)
    if not user:
        return HttpResponseRedirect('/')

    base = flowBase.getBase(request, 'volunteer')
    pageSet = paging.get(request.GET, len(user.article_link), displayCount=displayCount)
    entryList = [obj.rsplit(u',http://', 1) for obj in user.article_link[pageSet['entryOffset']:pageSet['entryOffset'] + displayCount]]

    template_values = {
            'isSelf':                   True if base['user'] == user.volunteer_id else False,
            'base':                     base,
            'volunteerBase':            flowBase.getVolunteerBase(user),
            'entryList':                entryList,
            'firstEntry':               entryList[0] if len(entryList) > 0 else None,
            'page':                     'space',
            'pageSet':                  pageSet,
            'queryString':              'volunteer_id=%s' % (user.volunteer_id.email()),
    }

    return render_to_response('volunteer/article_list.html', template_values)

def articleCreate(request):
    import re
    user = flowBase.getVolunteer(users.get_current_user())
    if not user:
        return HttpResponse(simplejson.dumps({'statusCode': 501, 'reason': 'No login'}), mimetype='application/json')
    itemList = request.POST.getlist('itemList')
    try:
        for item in itemList:
            # Ref: http://regexlib.com/RETester.aspx?regexp_id=96
            if re.match('^.+,(http://){2}[\w\-_]+(\.[\w\-_]+)+([\w\-\.,@?^=%&amp;:/~\+#]*[\w\-\@?^=%&amp;/~\+#])?$', item):
                user.article_link.insert(0, item.decode('UTF-8'))
        user.put()
    except:
        return HttpResponse(simplejson.dumps({'statusCode': 500, 'reason': str(sys.exc_info())}), mimetype='application/json')
    return HttpResponse(simplejson.dumps({'statusCode': 200, 'reason': 'success'}), mimetype='application/json')

def articleDelete(request):
    user = flowBase.getVolunteer(users.get_current_user())
    if not user:
        return HttpResponse(simplejson.dumps({'statusCode': 501, 'reason': 'No login'}), mimetype='application/json')
    itemId = int(request.GET.get('itemId', 0))
    if itemId >= 0:
        try:
            user.article_link.pop(itemId - 1)
            user.put()
        except:
            return HttpResponse(simplejson.dumps({'statusCode': 500, 'reason': str(sys.exc_info())}), mimetype='application/json')
        return HttpResponse(simplejson.dumps({'statusCode': 200, 'reason': 'success'}), mimetype='application/json')
    else:
        return HttpResponse(simplejson.dumps({'statusCode': 404, 'reason': 'Unknown action'}), mimetype='application/json')

def feedUriSave(request):
    user = flowBase.getVolunteer(users.get_current_user())
    if not user:
        return HttpResponse(simplejson.dumps({'statusCode': 501, 'reason': 'No login'}), mimetype='application/json')
    feedUri = request.POST.get('feedUri', None)
    if feedUri:
        try:
            user.saved_feed_link = feedUri
            user.put()
        except:
            return HttpResponse(simplejson.dumps({'statusCode': 500, 'reason': str(sys.exc_info())}), mimetype='application/json')
        return HttpResponse(simplejson.dumps({'statusCode': 200, 'reason': 'success'}), mimetype='application/json')
    else:
        return HttpResponse(simplejson.dumps({'statusCode': 404, 'reason': 'Unknown action'}), mimetype='application/json')
