# -*- coding: utf8 -*-

import datetime
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.shortcuts import render_to_response
from google.appengine.ext import db
from db import ddl
from common import paging
import flowBase

def mainPage(request): 
    if request.path=='/':
        return HttpResponseRedirect('/event/')
    intEventDisplayCount=10
    now = datetime.datetime.now()
    if 'cat' not in request.GET:
        return HttpResponseRedirect('/event/')
    if request.GET['cat'] == '1':
        eventTypeStr = u'新進'
        pageSet = paging.get(request.GET, ddl.EventProfile.gql('where status in (:1,:2,:3,:4) ORDER BY create_time DESC','approved','registrating','registration closed','on-going').count(1000), displayCount=intEventDisplayCount)
        eventAll = ddl.EventProfile.gql('where status in (:1,:2,:3,:4) ORDER BY create_time DESC','approved','registrating','registration closed','on-going').fetch(intEventDisplayCount, pageSet['entryOffset'])
    elif request.GET['cat'] == '2':
        eventTypeStr = u'即將額滿'
        pageSet = paging.get(request.GET, ddl.EventProfile.gql('where status in (:1,:2) ORDER BY volunteer_shortage ASC','approved','registrating').count(1000), displayCount=intEventDisplayCount)
        eventAll = ddl.EventProfile.gql('where status in (:1,:2) ORDER BY volunteer_shortage ASC','approved','registrating').fetch(intEventDisplayCount, pageSet['entryOffset'])
    elif request.GET['cat'] == '3':
        eventTypeStr = u'已完成'
        pageSet = paging.get(request.GET, ddl.EventProfile.gql('where status in (:1) ORDER BY update_time DESC','activity closed').count(1000), displayCount=intEventDisplayCount)
        eventAll = ddl.EventProfile.gql('where status in (:1) ORDER BY update_time DESC','activity closed').fetch(intEventDisplayCount, pageSet['entryOffset'])
    else:
        return HttpResponseRedirect('/event/')
    listActivityResult = []
    dictRecruitingResult = {}
      
    for event in eventAll:   
        listActivityResult.append(
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
    dic={'eventAll':listActivityResult,
         'base': flowBase.getBase(request, 'event'),
         'queryString':'cat=%s'%request.GET['cat'],
         'eventType':eventTypeStr,
         'pageSet': pageSet}
    return render_to_response('event/event-fullpage-list.html',dic)    

