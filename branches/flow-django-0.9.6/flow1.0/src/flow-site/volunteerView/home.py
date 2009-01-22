#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
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

def show(request, displayPhotoCount=8, displayBlogCount=6):
    if 'volunteer_id' not in request.GET:
        if users.get_current_user():
            userID = users.get_current_user()
        else:
            return HttpResponseRedirect('/')
    else:
        userID = cgi.escape(request.GET['volunteer_id'])
        if userID.find('@gmail.com') == -1:
            userID += '@gmail.com'
            userID = users.User(userID)

    # Picasa Web
    picasaUser = 'ckchien'
    service = gdata.photos.service.PhotosService()
    gdata.alt.appengine.run_on_appengine(service)
    photoFeeds = service.GetUserFeed(user=picasaUser, kind='photo', limit=displayPhotoCount).entry
    #photoFeeds.reverse()
    #photos = service.SearchUserPhotos(query='若水', user='ckchien').entry

    # Youtube
    vid = 'kt3JvQHQF-c'
    service = gdata.youtube.service.YouTubeService()
    gdata.alt.appengine.run_on_appengine(service)
    video = service.GetYouTubeVideoEntry(video_id=vid)
    #return HttpResponse(video, mimetype="text/xml")

    # Blogger
    blogID = 22301408
    service = gdata.blogger.service.BloggerService()
    gdata.alt.appengine.run_on_appengine(service)
    query = gdata.blogger.service.BlogPostQuery(blog_id=blogID)
    query.max_results = displayBlogCount
    blogFeeds = service.Get(query.ToUri())
    #return HttpResponse(blogFeeds.entry[0], mimetype="text/plain")

    user = db.GqlQuery('SELECT * FROM VolunteerProfile WHERE volunteer_id = :1', userID).get()
    if not user:
        pass
    userIM = user.im2volunteer.get()
    template_values = {
            'base':                     flowBase.getBase(request, user),
            'sex':                      user.sex,
            'photoFeeds':               photoFeeds,
            'video':                    video,
    }
    response = render_to_response('volunteer/profile_home.html', template_values)

    return response

