from django.http import HttpResponse
from django.shortcuts import render_to_response
#from django.template import TemplateDoesNotExists
import datetime
from google.appengine.ext import db
from db import ddl3

def mainPage(request): 
        
    now = datetime.datetime.now()
    event1 = ddl3.EventProfile.gql('where status in (:1,:2)','approved','recruiting').fetch(5)
    event2 = ddl3.EventProfile.gql('where status in (:1,:2)','approved','recruiting').fetch(5)
    event3 = ddl3.EventProfile.gql('where status in (:1)','activity closed').fetch(5)
    #recruitings = db.GqlQuery("SELECT * FROM RecruitingSpec")
    listActivityResult1 = []
    listActivityResult2 = []
    listActivityResult3 = []
    dictRecruitingResult = {}
    #for recruiting in recruitings:
     #   dictRecruitingResult[recruiting.activity_id]=recruiting.head_count_required
      
    for event in event1:   
        if now < event.end_time:
            listActivityResult1.append(
             {'event_id':event.event_id,
             'event_name':event.event_name,
             'originator':event.originator,
             'create_time':event.create_time.strftime('%Y-%m-%d %H:%M'),
             'start_time':event.start_time.strftime('%Y-%m-%d %H:%M'),
             'event_region':u','.join(event.event_region),
             'description':event.description,
             'event_key':str(event.key()),
             }
             )
    
  
    for event in event2:
        intLackPeople= event.volunteer_req - event.approved_count
        listActivityResult2.append(
            {'event_id':event.event_id,
             'event_name':event.event_name,
             'originator':event.originator,
             'create_time':event.create_time.strftime('%Y-%m-%d %H:%M'),
             'start_time':event.start_time.strftime('%Y-%m-%d %H:%M'),
             'event_region':u','.join(event.event_region),
             'description':event.description,
             'lackpeople':intLackPeople,
             'event_key':str(event.key()),
             #'headcount':dictRecruitingResult[event.event_id]
             }
             )
    for event in event3:   
        listActivityResult3.append(
         {'event_id':event.event_id,
         'event_name':event.event_name,
         'originator':event.originator,
         'create_time':event.create_time.strftime('%Y-%m-%d %H:%M'),
         'start_time':event.start_time.strftime('%Y-%m-%d %H:%M'),
         'event_region':u','.join(event.event_region),
         'description':event.description,
          'event_key':str(event.key()),
         }
        )

    
    return render_to_response('event/event-list.html',{'event1':listActivityResult1,'event2':listActivityResult2,'event3':listActivityResult3})    

