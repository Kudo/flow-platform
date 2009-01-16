#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cgi
from datetime import datetime
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from google.appengine.ext import db
from google.appengine.api import users
import atom.url
import gdata.alt.appengine
import gdata.photos, gdata.photos.service
import gdata.youtube, gdata.youtube.service
import gdata.blogger, gdata.blogger.service
import flowBase
from db.ddl import VolunteerProfile, VolunteerIm

def show(request, displayAlbumCount=2, displayBlogCount=5):
    if 'volunteer_id' not in request.GET:
        if users.get_current_user():
            userID = users.get_current_user()
            isSelf = True
        else:
            return HttpResponseRedirect('/')
    else:
        userID = cgi.escape(request.GET['volunteer_id'])
        if userID.find('@gmail.com') == -1:
            userID += '@gmail.com'
            userID = users.User(userID)
            isSelf = True if users.get_current_user() == userID else False

    user = db.GqlQuery('SELECT * FROM VolunteerProfile WHERE volunteer_id = :1', userID).get()
    if not user:
        pass

    # Picasa Web
    picasaUser = 'ckchien'
    service = gdata.photos.service.PhotosService()
    gdata.alt.appengine.run_on_appengine(service)
    albumFeeds = service.GetUserFeed(user=picasaUser).entry[:displayAlbumCount]
    albums = [{'albumFeed': album, 'photoFeeds': service.GetFeed(album.GetPhotosUri()).entry} for album in albumFeeds] 
    #return HttpResponse(albums[0]['photoFeeds'][0], mimetype="text/xml")
    #photos = service.SearchUserPhotos(query='若水', user='ckchien').entry
    del albumFeeds

    # Youtube
    vid = 'kt3JvQHQF-c'
    service = gdata.youtube.service.YouTubeService()
    gdata.alt.appengine.run_on_appengine(service)
    video = service.GetYouTubeVideoEntry(video_id=vid)
    videoDate = datetime.strptime(video.published.text, '%Y-%m-%dT%H:%M:%S.000Z')
    #return HttpResponse(video, mimetype="text/xml")

    # Blogger
    blogID = 22301408
    service = gdata.blogger.service.BloggerService()
    gdata.alt.appengine.run_on_appengine(service)
    query = gdata.blogger.service.BlogPostQuery(blog_id=blogID)
    query.max_results = displayBlogCount
    blogFeeds = service.Get(query.ToUri())
    #return HttpResponse(blogFeeds.entry[0], mimetype="text/plain")


    template_values = {
            'isSelf':                   isSelf,
            'base':                     flowBase.getBase(request, user),
            'albums':                   albums,
            'video':                    video,
            'videoDate':                videoDate,
            'blogFeeds':                blogFeeds.entry,

    }
    response = render_to_response('volunteer/profile_space.html', template_values)

    return response
