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

def edit(request):
    if request.method == 'POST':
        npo_id = cgi.escape(request.GET['npo_id'])
        if 'cancel' in request.POST:
            return HttpResponseRedirect("npo_info.html?npo_id=" + npo_id)
        
        form = NpoProfileForm(data=request.POST)
        if form.is_valid():
            npoProfile = db.GqlQuery('SELECT * FROM NpoProfile WHERE npo_id = :1', npo_id).get()
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
    if 'npo_id' not in request.GET:
        return HttpResponseRedirect('/')
    else:
        npo_id = cgi.escape(request.GET['npo_id'])
       
    npoProfile = db.GqlQuery('SELECT * FROM NpoProfile WHERE npo_id = :1', npo_id).get()
    
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
    }
    response = render_to_response('npo/manage_edit_info.html', template_values)
    return response    

displayCount = 10
def memberList(request):
    if 'npo_id' not in request.GET:
        return HttpResponseRedirect('/')
    else:
        npo_id = cgi.escape(request.GET['npo_id'])
    
    npoProfile = db.GqlQuery('SELECT * FROM NpoProfile WHERE npo_id = :1', npo_id).get()
    
    members = db.get(npoProfile.members)
    numOfMembers = len(members)
    pageSet = paging.get(request.GET, numOfMembers, displayCount=displayCount)
    
    # members showed in left column
    '''
    leftMembers = members[:]
    row1 = []
    for i in range(0, 3):
        if len(leftMembers) == 0:
            break
        row1.append(random.choice(leftMembers))
        leftMembers.remove(row1[i])
    
    row2 = []
    for i in range(0, 3):
        if len(leftMembers) == 0:
            break
        row2.append(random.choice(leftMembers))
        leftMembers.remove(row2[i])
        
    '''
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

displayPhotoCount = 8
displayArticleCount = 10
displayNpoEventCount = 2

def showHome(request):
    if 'npo_id' not in request.GET:
        return HttpResponseRedirect('/')
    else:
        npo_id = cgi.escape(request.GET['npo_id'])
        
#    user = users.User("john_doe@gmail.com")
#    now = datetime.datetime.utcnow()
#    npo = NpoProfile(npo_name="Holy Shoot",founder="Rick Wang", google_acct=user, country="ROC", postal="104", state="Taiwan", city="Taipei",
#                     district="Nangang", founding_date=datetime.date(1980, 1, 1), authority="GOV", tag=["wild lives", "marines"],
#                     status="new application", docs_link=["Timbuck2"], npo_rating=1, create_time=now, update_time=now, news_list=[db.Text(u"最新消息第一條"), db.Text(u"最新消息第二條"), db.Text(u"最新消息第三條")])
# 
#    npo.put()
#  
#    user      = users.User("jane_doe@gmail.com")
#    now       = datetime.datetime.utcnow()
#    volunteer = VolunteerProfile(volunteer_id=user, id_no="A123456789", volunteer_last_name="Doe", volunteer_first_name="Jacy", gmail=user.email(),
#                                 date_birth=datetime.date(1970, 2, 1), expertise=["PR"], sex="Female", phone_no="02-1234-5678", resident_country="ROC",
#                                 resident_postal="104", resident_state="Taiwan", resident_city="Taipei", resident_district="Shilin",
#                                 prefer_region=[], prefer_zip=[], prefer_target=[], prefer_field=[], prefer_group=[],
#                                 create_time=now, update_time=now, volunteer_rating=80, status="normal" , search_text=u"測試中文字 test. ngram 屋啦啦 中英文English")
#
#    volunteer.put()
#    npoProfile = db.GqlQuery('SELECT * FROM NpoProfile WHERE npo_id = :1', npo_id).get()
#    npoProfile.members.append(volunteer.key())
#    
#    npoProfile.put()
#

    npoProfile = db.GqlQuery('SELECT * FROM NpoProfile WHERE npo_id = :1', npo_id).get()
    members = db.get(npoProfile.members)
    eventList = npoProfile.event2npo.fetch(displayNpoEventCount)
    
#    npoContact = NpoContact(npo_profile_ref = npoProfile,
#                            contact_type = "Major",
#                            contact_name = "Contact Name",
#                            contact_email= "npo@email.com",
#                            volunteer_id = users.User("john_doe@gmail.com"))
#    npoContact.put()

#    npoPhone = NpoPhone(npo_profile_ref = npoProfile,
#                        phone_type = "Fixed",
#                        phone_no = "0912345678")
#    npoPhone.put()
#    
#    npoPhone = NpoPhone(npo_profile_ref = npoProfile,
#                        phone_type = "Fax",
#                        phone_no = "0234567890")
#    npoPhone.put()
    
    # recently attended members
    recentMembers = members[:]
    latestMember = None
    if (len(recentMembers) > 0):
        latestMember = recentMembers[-1]
        recentMembers = recentMembers[-5:-1]
        recentMembers.reverse()
    
    # members showed in left column
    leftMembers = members[:]
    row1 = []
    for i in range(0, 3):
        if len(leftMembers) == 0:
            break
        row1.append(random.choice(leftMembers))
        leftMembers.remove(row1[i])
    
    row2 = []
    for i in range(0, 3):
        if len(leftMembers) == 0:
            break
        row2.append(random.choice(leftMembers))
        leftMembers.remove(row2[i])

    import atom.url
    import gdata.alt.appengine
    import gdata.photos, gdata.photos.service
    import gdata.youtube, gdata.youtube.service

    # Picasa Web
    picasaUser = 'ckchien'
    service = gdata.photos.service.PhotosService()
    gdata.alt.appengine.run_on_appengine(service)
    photoFeeds = service.GetUserFeed(user=picasaUser, kind='photo', limit=displayPhotoCount).entry
    #photoFeeds.reverse()
    #photos = service.SearchUserPhotos(query='若水', user='ckchien').entry

    # Youtube
    video = None
    videoDate = None
    if len(npoProfile.video_link) > 0:
        vid = npoProfile.video_link[0]
        service = gdata.youtube.service.YouTubeService()
        gdata.alt.appengine.run_on_appengine(service)
        video = service.GetYouTubeVideoEntry(video_id=vid)

    
    template_values = {
            'npoProfile': npoProfile,
            'recentMembers': recentMembers,
            'latestMember': latestMember,
            'leftMembersRow1': row1,
            'leftMembersRow2': row2,
            'numOfMembers': len(members),
            'eventList': eventList,
            'page': 'home',
            'base':flowBase.getBase(request, 'npo'),
            'feedUri':                  npoProfile.saved_feed_link or '',
            'photoFeeds':               photoFeeds,
            'video':                    video,
            'npoBase':                  flowBase.getNpoBase(npoProfile),
            'articleList':              [obj.rsplit(u',http://', 1) for obj in npoProfile.article_link][:displayArticleCount],
     }
    response = render_to_response('npo/npo_home.html', template_values)
    return response

def showInfo(request):
    if 'npo_id' not in request.GET:
        return HttpResponseRedirect('/')
    else:
        npo_id = cgi.escape(request.GET['npo_id'])

    npoProfile = db.GqlQuery('SELECT * FROM NpoProfile WHERE npo_id = :1', npo_id).get()

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

displayCount = 10
def showEvents(request):
    if 'npo_id' not in request.GET:
        return HttpResponseRedirect('/')
    else:
        npo_id = cgi.escape(request.GET['npo_id'])
        
    npoProfile = db.GqlQuery('SELECT * FROM NpoProfile WHERE npo_id = :1', npo_id).get()
    pageSet = paging.get(request.GET, npoProfile.event2npo.count(), displayCount=displayCount)
    eventAll = npoProfile.event2npo.fetch(displayCount, pageSet['entryOffset'])
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
     }
    response = render_to_response('npo/npo_events.html', template_values)
    return response

def leftColumn(npoProfile, numOfMembers, row1, row2):
#    if 'npo_id' not in request.GET:
#        return HttpResponseRedirect('/')
#    else:
#        npo_id = cgi.escape(request.GET['npo_id'])
#        
#    npoProfile = db.GqlQuery('SELECT * FROM NpoProfile WHERE npo_id = :1', npo_id).get()
    members = db.get(npoProfile.members)
    numOfMembers = len(members)     
    
    # members showed in left column
    leftMembers = members[:]
#    row1 = []
    for i in range(0, 3):
        if len(leftMembers) == 0:
            break
        row1.append(random.choice(leftMembers))
        leftMembers.remove(row1[i])
    
#    row2 = []
    for i in range(0, 3):
        if len(leftMembers) == 0:
            break
        row2.append(random.choice(leftMembers))
        leftMembers.remove(row2[i])
        
#    template_values = {
#            'npoProfile': npoProfile,
#            'leftMembersRow1': row1,
#            'leftMembersRow2': row2,
#            'numOfMembers': len(members),
#     }
#    response = render_to_response('npo/profile_leftcolumn.html', template_values)
#    return response
    return
    
