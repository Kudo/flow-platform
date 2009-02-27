import datetime
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.shortcuts import render_to_response
from google.appengine.ext import db
from db import ddl
import flowBase

def mainPage(request): 
    if request.path=='/':
        return HttpResponseRedirect('/event/')
    
    now = datetime.datetime.now()
    event1 = ddl.EventProfile.gql('where status in (:1,:2) ORDER BY create_time DESC','approved','recruiting').fetch(5)
    event2 = ddl.EventProfile.gql('where status in (:1,:2) ORDER BY volunteer_shortage ASC','approved','recruiting').fetch(5)
    #event2 = ddl.EventProfile.gql('where status in (:1,:2) ORDER BY (:3)','approved','recruiting','volunteer_req - approved_count').fetch(5)
    event3 = ddl.EventProfile.gql('where status in (:1) ORDER BY update_time DESC','activity closed').fetch(5)
    listActivityResult1 = []
    listActivityResult2 = []
    listActivityResult3 = []
    dictRecruitingResult = {}
      
    for event in event1:   
        if now < event.end_time:
            listActivityResult1.append(
             {'event_id':event.event_id,
             'event_name':event.event_name,
             'originator':event.npo_profile_ref.npo_name,
             'create_time':event.create_time.strftime('%Y-%m-%d %H:%M'),
             'start_time':event.start_time.strftime('%Y-%m-%d %H:%M'),
             'event_region':u','.join(event.event_region),
             'description':event.description,
             'event_key':str(event.key()),
             }
             )
    
  
    for event in event2:
        #intLackPeople= event.volunteer_req - event.approved_count
        listActivityResult2.append(
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
    for event in event3:   
        listActivityResult3.append(
         {'event_id':event.event_id,
         'event_name':event.event_name,
         'originator':event.npo_profile_ref.npo_name,
         'create_time':event.create_time.strftime('%Y-%m-%d %H:%M'),
         'start_time':event.start_time.strftime('%Y-%m-%d %H:%M'),
         'event_region':u','.join(event.event_region),
         'description':event.description,
          'event_key':str(event.key()),
         }
        )

    
    return render_to_response('event/event-list.html',{'event1':listActivityResult1,'event2':listActivityResult2,'event3':listActivityResult3, 'base': flowBase.getBase(request)})    

