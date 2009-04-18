#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import datetime
import cgi
import re
import string
import random
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from google.appengine.ext import db
from google.appengine.api import users
from db.ddl import NpoProfile
from db.ddl import NpoContact
from db.ddl import NpoPhone
import flowBase
from common import paging
try:
    from django import newforms as forms
except ImportError:
    from django import forms
from google.appengine.ext.db import djangoforms

class NpoProfileForm(djangoforms.ModelForm):
    txtFounder                    = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'field text medium'}))
    textareaIntro                 = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'field textarea medium', 'cols': '50', 'rows': '10'}))

#    class Meta:
#        model = NpoProfile
#        fields = [
##                  'volunteer_first_name', 'volunteer_last_name', 'sex', 'resident_city', 'logo', 'school', 'organization', 'title',
##                  'cellphone_no', 'blog', 'expertise',
#                  'brief_intro',
#                 ]

def edit(request, npoid):
    npoProfile = flowBase.getNpo(npo_id=npoid)
    if not npoProfile:
        return HttpResponseRedirect('/')

    if request.method == 'POST':
        form = NpoProfileForm(data=request.POST)
        if form.is_valid():
            npoProfile.npo_name = request.POST['txtGroupName']
            npoProfile.founder = form.clean_data['txtFounder']
            npoProfile.brief_intro = form.clean_data['textareaIntro']
            npoProfile.website = request.POST['txtHomePage']
            npoProfile.authority = request.POST['txtApproveGov']
            del npoProfile.service_region[0]
            npoProfile.service_region.insert(0, request.POST['txtServiceArea'])
            del npoProfile.service_target[0]
            npoProfile.service_target.insert(0, request.POST['txtServiceTarget'])
            del npoProfile.service_field[0]
            npoProfile.service_field.insert(0, request.POST['txtServiceItem'])
            npoProfile.bank_acct_no = request.POST['txtTransferAccountNo']
            npoProfile.bank_acct_name = request.POST['txtTransferAccountTitle']
            npoProfileKey = npoProfile.put()
            npoContact = NpoContact.all().filter('npo_profile_ref =', npoProfileKey).get()
            if (npoContact != None):
                npoContact.contact_name = request.POST['txtContact']
                npoContact.put()
                
            npoPhoneFixed = db.GqlQuery('SELECT * FROM NpoPhone WHERE npo_profile_ref = :1 AND phone_type = :2', npoProfileKey, 'Fixed').get()
            if (npoPhoneFixed == None):
                npoPhoneFixed = NpoPhone(npo_profile_ref=npoProfileKey, phone_type="Fixed", phone_no=u"02-xxxxxxxx")
            npoPhoneFixed.phone_no = request.POST['txtPhone']
            npoPhoneFixed.put()
            
            npoPhoneFax = db.GqlQuery('SELECT * FROM NpoPhone WHERE npo_profile_ref = :1 AND phone_type = :2', npoProfileKey, 'Fax').get()
            if (npoPhoneFax == None):
                npoPhoneFax = NpoPhone(npo_profile_ref=npoProfileKey, phone_type="Fax", phone_no=u"02-xxxxxxxx")
            npoPhoneFax.phone_no = request.POST['txtFax']
            npoPhoneFax.put()
            
            return HttpResponseRedirect("npo_info.html?npo_id=" + npo_id)
      
#    else:
    fixedPhone = ""
    faxPhone = ""
    for phone in npoProfile.phones2npo:
        if (phone.phone_type == "Fixed"):
            fixedPhone = phone.phone_no
        if (phone.phone_type == "Fax"):
            faxPhone = phone.phone_no
        
    npoContact = ""        
    for contact in npoProfile.contacts2npo:
        if (contact.contact_name != ""):
            npoContact = contact
            break
        
    template_values = {
           'path': request.path,
           'npoProfile': npoProfile,
           'npoContact': npoContact,
           'fixedPhone': fixedPhone,
           'faxPhone': faxPhone,
           'service_region': npoProfile.service_region[0],
           'service_target': npoProfile.service_target[0],
           'service_field': npoProfile.service_field[0],
           'base':flowBase.getBase(request, 'npo'),
           'npoBase': flowBase.getNpoBase(npoProfile),
           'page': 'info',
    }
    response = render_to_response('npo/manage_edit_info.html', template_values)
    return response    

def memberList(request, npoid, displayCount = 10):
    npoProfile = flowBase.getNpo(npo_id=npoid)
    if not npoProfile:
        return HttpResponseRedirect('/')
    
    members = db.get(npoProfile.members)
    numOfMembers = len(members)
    pageSet = paging.get(request.GET, numOfMembers, displayCount=displayCount)
    memberList = members[pageSet['entryOffset']:displayCount]
    
    template_values = {
        'pageSet': pageSet,
        'npoProfile': npoProfile,
        'memberList': memberList,
        'page': 'volunteers',
        'npoBase': flowBase.getNpoBase(npoProfile),
        'base':flowBase.getBase(request, 'npo')
    }
    response = render_to_response('npo/npo_volunteers.html', template_values)
    return response

displayMemberCount = 3
displayAlbumCount = 2
displayPhotoCount = 5
displayArticleCount = 10
displayNpoEventCount = 2

def showHome(request, npoid):
    npoProfile = flowBase.getNpo(npo_id=npoid)
    if not npoProfile:
        return HttpResponseRedirect('/')

    members = db.get(npoProfile.members)
    eventList = npoProfile.event2npo.fetch(displayNpoEventCount)

    for event in eventList:
        if len(event.event_name) > 8:
            event.event_name = event.event_name[:8] + u'...'
        if len(event.description) > 20:
            event.description = event.description[:20] + u'...'
    
    import atom.url
    import gdata.alt.appengine
    import gdata.photos.service
    import gdata.youtube.service
    from db.ddl import VolunteerProfile

    # recently attended members
    recentMembers = []
    for member in npoProfile.members[0 - displayMemberCount:]:
        vol = VolunteerProfile.get(member)
        if len(vol.nickname) > 10:
            vol.nickname = vol.nickname[:10] + u'...'
        recentMembers.append(vol)
    recentMembers.reverse()

    # Picasa Web
    albums = []
    service = gdata.photos.service.PhotosService()
    gdata.alt.appengine.run_on_appengine(service)
    for albumLink in npoProfile.photo_link[:displayAlbumCount]:
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
    for vid in npoProfile.video_link:
        try:
            video = service.GetYouTubeVideoEntry(video_id=vid)
        except:
            continue
        break
    
    template_values = {
            'isAdmin':                  True if flowBase.isNpoAdmin(npo=npoProfile) else False,
            'npoProfile':               npoProfile,
            'recentMembers':            recentMembers,
            'eventList':                eventList,
            'page':                     'home',
            'base':                     flowBase.getBase(request, 'npo'),
            'albumUri':                 npoProfile.saved_picasa_link or '',
            'feedUri':                  npoProfile.saved_feed_link or '',
            'albums':                   albums,
            'video':                    video,
            'npoBase':                  flowBase.getNpoBase(npoProfile),
            'articleList':              [obj.rsplit(u',http://', 1) for obj in npoProfile.article_link][:displayArticleCount],
     }
    response = render_to_response('npo/npo_home.html', template_values)
    return response

def showInfo(request, npoid):
    npoProfile = flowBase.getNpo(npo_id=npoid)
    if not npoProfile:
        return HttpResponseRedirect('/')

    fixedPhone = ""
    faxPhone = ""
    for phone in npoProfile.phones2npo:
        if (phone.phone_type == "Fixed"):
            fixedPhone = phone.phone_no
        if (phone.phone_type == "Fax"):
            faxPhone = phone.phone_no


    template_values = {
            'npoProfile': npoProfile,
            'npoContact': npoProfile.contacts2npo,
            'fixedPhone': fixedPhone,
            'faxPhone': faxPhone,
            'service_region': npoProfile.service_region[0],
            'service_target': npoProfile.service_target[0],
            'service_field': npoProfile.service_field[0],
            'page': 'home',
            'base':flowBase.getBase(request, 'npo'),
            'npoBase': flowBase.getNpoBase(npoProfile),
     }
    response = render_to_response('npo/npo_info.html', template_values)
    return response

def showEventsRedir(request, npoid):
    return showEvents(request, npoid, "")

def showEvents(request, npoid, status, displayCount = 10):
    npoProfile = flowBase.getNpo(npo_id=npoid)
    if not npoProfile:
        return HttpResponseRedirect('/')

    now = datetime.datetime.now()
    if status != "history":
        queryObj = npoProfile.event2npo.filter('start_time >=', now)
    else:
        queryObj = npoProfile.event2npo.filter('start_time <', now)

    pageSet = paging.get(request.GET, queryObj.count(), displayCount=displayCount)
    eventAll = queryObj.fetch(displayCount, pageSet['entryOffset'])
    eventList = []
    
    for event in eventAll:   
        eventList.append(
         {'event_id':event.event_id,
         'event_name':event.event_name,
         'originator':event.npo_profile_ref.npo_name,
         'create_time':event.create_time.strftime('%Y-%m-%d %H:%M'),
         'start_time':event.start_time.strftime('%Y-%m-%d %H:%M'),
         'event_region':u','.join(event.event_region),
         'description':event.description,
         'registered_count':event.registered_count,
         'approved_count':event.approved_count,
         'volunteer_shortage':event.volunteer_shortage,
         'event_key':str(event.key())}
         )

            
    template_values = {
            'npoProfile': npoProfile,
            'eventList': eventList,
            'pageSet': pageSet,
            'page': 'events',
            'base':flowBase.getBase(request, 'npo'),
            'npoBase': flowBase.getNpoBase(npoProfile),
            'status': status
     }
    response = render_to_response('npo/npo_events.html', template_values)
    return response
