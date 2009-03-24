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
    
    if request.GET['cat'] == '1':
        pageSet = paging.get(request.GET, ddl.EventProfile.gql('where status in (:1,:2) ORDER BY create_time DESC','approved','recruiting').count(1000), displayCount=intEventDisplayCount)
        eventAll = ddl.EventProfile.gql('where status in (:1,:2) ORDER BY create_time DESC','approved','recruiting').fetch(intEventDisplayCount, pageSet['entryOffset'])
    elif request.GET['cat'] == '2':
        pageSet = paging.get(request.GET, ddl.EventProfile.gql('where status in (:1,:2) ORDER BY volunteer_shortage ASC','approved','recruiting').count(1000), displayCount=intEventDisplayCount)
        eventAll = ddl.EventProfile.gql('where status in (:1,:2) ORDER BY volunteer_shortage ASC','approved','recruiting').fetch(intEventDisplayCount, pageSet['entryOffset'])
    elif request.GET['cat'] == '3':
        pageSet = paging.get(request.GET, ddl.EventProfile.gql('where status in (:1) ORDER BY update_time DESC','activity closed').count(1000), displayCount=intEventDisplayCount)
        eventAll = ddl.EventProfile.gql('where status in (:1) ORDER BY update_time DESC','activity closed').fetch(intEventDisplayCount, pageSet['entryOffset'])
    
    listActivityResult = []
    dictRecruitingResult = {}
      
    for event in eventAll:   
        if (request.GET['cat'] == 1 and now < event.end_time) or request.GET['cat'] != 1:
            listActivityResult.append(
             {'event_id':event.event_id,
             'event_name':event.event_name,
             'originator':event.npo_profile_ref.npo_name,
             'create_time':event.create_time.strftime('%Y-%m-%d %H:%M'),
             'start_time':event.start_time.strftime('%Y-%m-%d %H:%M'),
             'event_region':u','.join(event.event_region),
             'description':event.description,
             'lackpeople':event.volunteer_shortage,
             'event_key':str(event.key()),
             }
             )
    
    return render_to_response('event/event-fullpage-list.html',{'eventAll':listActivityResult, 'base': flowBase.getBase(request, 'event'), 'pageSet': pageSet})    

