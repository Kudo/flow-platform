#-*- coding: cp950 -*-
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import TemplateDoesNotExist
from google.appengine.ext import db
from db import ddl
import flowBase
import datetime
from django.http import HttpResponseRedirect
import logging
import sys,cgi,re,time,os

DIR_PATH = r'c:\Program Files\Google\google_appengine'
EXTRA_PATHS = [
  DIR_PATH,
  os.path.join(DIR_PATH, 'lib', 'django'),
  os.path.join(DIR_PATH, 'lib', 'webob'),
  os.path.join(DIR_PATH, 'lib', 'yaml', 'lib'),
]
sys.path = EXTRA_PATHS + sys.path

from google.appengine.api import users


dicRule = {'new application'        :{'modify':'','recruit':'disabled','validate':'disabled','close':'disabled','cancel':''},
           'approved'               :{'modify':'','recruit':'disabled','validate':'disabled','close':'disabled','cancel':''},
           'announced'              :{'modify':'','recruit':'disabled','validate':'disabled','close':'disabled','cancel':''},
           'authenticating'         :{'modify':'','recruit':'disabled','validate':'disabled','close':'disabled','cancel':''},
           'authenticated'          :{'modify':'','recruit':'','validate':'','close':'disabled','cancel':''},
           'registrating'           :{'modify':'','recruit':'','validate':'','close':'disabled','cancel':''},
           'recruiting'             :{'modify':'','recruit':'','validate':'','close':'disabled','cancel':''},
           'registration closed'    :{'modify':'','recruit':'disabled','validate':'disabled','close':'disabled','cancel':'disabled'},
           'on-going'               :{'modify':'','recruit':'','validate':'','close':'disabled','cancel':'disabled'},
           'filling polls'          :{'modify':'','recruit':'disabled','validate':'disabled','close':'disabled','cancel':'disabled'},
           'activity closed'        :{'modify':'disabled','recruit':'disabled','validate':'disabled','close':'','cancel':'disabled'},
           'case-closed reporting'  :{'modify':'disabled','recruit':'disabled','validate':'disabled','close':'disabled','cancel':'disabled'},
           'cancelled'              :{'modify':'disabled','recruit':'disabled','validate':'disabled','close':'disabled','cancel':'disabled'},
           'abusive usage'          :{'modify':'disabled','recruit':'disabled','validate':'disabled','close':'disabled','cancel':'disabled'}
           }

'''dicStatus = {'new application'      :'新申請',
           'approved'               :'審核通過',
           'announced'              :'已公告',
           'authenticating'         :'手機認證中',
           'authenticated'          :'手機認證通過',
           'registrating'           :'開放註冊中',
           'recruiting'             :'招募中',
           'registration closed'    :'停止註冊',
           'on-going'               :'活動執行中',
           'filling polls'          :'填寫問卷',
           'activity closed'        :'活動已結束',
           'case-closed reporting'  :'活動結案報告',
           'cancelled'              :'活動已取消',
           'abusive usage'          :'不當使用'
           }
'''
dicStatus = {'new application'      :'new application',
           'approved'               :'approved',
           'announced'              :'announced',
           'authenticating'         :'authenticating',
           'authenticated'          :'authenticated',
           'registrating'           :'registrating',
           'recruiting'             :'recruiting',
           'registration closed'    :'registration closed',
           'on-going'               :'on-going',
           'filling polls'          :'filling polls',
           'activity closed'        :'activity closed',
           'case-closed reporting'  :'case-closed reporting',
           'cancelled'              :'cancelled',
           'abusive usage'          :'abusive usage'
           }
def showEvent(request):
    # Retrieve Events from Database
    eventKey=request.GET.get('id')
    event=db.get(db.Key(eventKey))
    dicData={   "event_name": event.event_name,
                "description": event.description,
                "originator":event.originator,
                "event_region": event.event_region,
                "event_hours" : event.event_hours,
                "event_target": event.event_target,
                "event_field": event.event_field,
                "create_time":event.create_time,
                "category":event.category,
                "start_time": event.start_time.strftime('%Y-%m-%d %H:%M'),
                "end_time" : event.end_time.strftime('%Y-%m-%d %H:%M'),
                "reg_start_time" : event.reg_start_time.strftime('%Y-%m-%d %H:%M'),
                "reg_end_time": event.reg_end_time.strftime('%Y-%m-%d %H:%M'),
                "objective": event.objective,
                "summary":event.summary,
                "event_id":event.event_id,
                "expense": event.expense,
                "registration_fee": event.registration_fee,
                "registered_volunteer": event.registered_volunteer,
                "registered_count": event.registered_count,
                "approved_volunteer": event.approved_volunteer,
                "approved_count": event.approved_count,
                "status": event.status,
                "approved": event.approved,
                "approved_time": event.approved_time,
                "attachment_links": event.attachment_links,
                "tag": event.tag,
                "max_age": event.max_age,
                "min_age": event.min_age,
                "sex": event.sex,
                "female_req": event.female_req,
                "male_req" : event.male_req,
                "volunteer_req": event.volunteer_req,
                "join_flow_plan": event.join_flow_plan,
                "sentiments": event.sentiments,
                "event_rating": event.event_rating,
                "npo_event_rating": event.npo_event_rating,
                "event_album_link": event.event_album_link,
                "event_video_link": event.event_video_link,
                "event_blog_link": event.event_blog_link,
                "create_time": event.create_time.strftime('%Y-%m-%d %H:%M'),
                "update_time": event.update_time.strftime('%Y-%m-%d %H:%M'),
                "id_key" : eventKey
            }
    intVolunteerNeeded = event.volunteer_req - event.approved_count
    if dicData["status"] == "recruiting" or dicData["status"] == "approved":
        return render_to_response(r'event/event-info.html', {'event' : dicData, 'base': flowBase.getBase(request), 'status' : dicStatus[event.status], 'needed': str(intVolunteerNeeded)})
    else:
        return render_to_response(r'event/event-info-noapply.html', {'event' : dicData, 'base': flowBase.getBase(request)})

def applyEvent(request):
    eventKey=request.POST.get('event_id')
    #return HttpResponse(str(eventKey))
    event=db.get(db.Key(eventKey))
    
    dicData={"event_name": event.event_name,
            "description": event.description,
            "originator":event.originator,
            "event_region": event.event_region,
            "event_hours" : event.event_hours,
            "event_target": event.event_target,
            "event_field": event.event_field,
            "create_time":event.create_time,
            "category":event.category,
            "start_time": event.start_time.strftime('%Y-%m-%d %H:%M'),
            "end_time" : event.end_time.strftime('%Y-%m-%d %H:%M'),
            "reg_start_time" : event.reg_start_time.strftime('%Y-%m-%d %H:%M'),
            "reg_end_time": event.reg_end_time.strftime('%Y-%m-%d %H:%M'),
            "objective": event.objective,
            "summary":event.summary,
            "event_id":event.event_id,
            "expense": event.expense,
            "registration_fee": event.registration_fee,
            "registered_volunteer": event.registered_volunteer,
            "registered_count": event.registered_count,
            "approved_volunteer": event.approved_volunteer,
            "approved_count": event.approved_count,
            "status": event.status,
            "approved": event.approved,
            "approved_time": event.approved_time,
            "attachment_links": event.attachment_links,
            "tag": event.tag,
            "max_age": event.max_age,
            "min_age": event.min_age,
            "sex": event.sex,
            "female_req": event.female_req,
            "male_req" : event.male_req,
            "volunteer_req": event.volunteer_req,
            "join_flow_plan": event.join_flow_plan,
            "sentiments": event.sentiments,
            "event_rating": event.event_rating,
            "npo_event_rating": event.npo_event_rating,
            "event_album_link": event.event_album_link,
            "event_video_link": event.event_video_link,
            "event_blog_link": event.event_blog_link,
            "create_time": event.create_time.strftime('%Y-%m-%d %H:%M'),
            "update_time": event.update_time.strftime('%Y-%m-%d %H:%M')
            }
    intVolunteerNeeded = event.volunteer_req - event.approved_count        
    return render_to_response(r'event/event-apply.html', {'event' : dicData, 'base': flowBase.getBase(request), 'status' : dicStatus[event.status], 'needed': str(intVolunteerNeeded), 'event_id': str(eventKey)})

def mailToFriend(request):
    eventKey=request.POST.get('event_id')
    #return HttpResponse(str(eventKey))
    event=db.get(db.Key(eventKey))
    
    dicData={   "event_name": event.event_name,
            "description": event.description,
            "originator":event.originator,
            "event_region": event.event_region,
            "event_hours" : event.event_hours,
            "event_target": event.event_target,
            "event_field": event.event_field,
            "create_time":event.create_time,
            "category":event.category,
            "start_time": event.start_time.strftime('%Y-%m-%d %H:%M'),
            "end_time" : event.end_time.strftime('%Y-%m-%d %H:%M'),
            "reg_start_time" : event.reg_start_time.strftime('%Y-%m-%d %H:%M'),
            "reg_end_time": event.reg_end_time.strftime('%Y-%m-%d %H:%M'),
            "objective": event.objective,
            "summary":event.summary,
            "event_id":event.event_id,
            "expense": event.expense,
            "registration_fee": event.registration_fee,
            "registered_volunteer": event.registered_volunteer,
            "registered_count": event.registered_count,
            "approved_volunteer": event.approved_volunteer,
            "approved_count": event.approved_count,
            "status": event.status,
            "approved": event.approved,
            "approved_time": event.approved_time,
            "attachment_links": event.attachment_links,
            "tag": event.tag,
            "max_age": event.max_age,
            "min_age": event.min_age,
            "sex": event.sex,
            "female_req": event.female_req,
            "male_req" : event.male_req,
            "volunteer_req": event.volunteer_req,
            "join_flow_plan": event.join_flow_plan,
            "sentiments": event.sentiments,
            "event_rating": event.event_rating,
            "npo_event_rating": event.npo_event_rating,
            "event_album_link": event.event_album_link,
            "event_video_link": event.event_video_link,
            "event_blog_link": event.event_blog_link,
            "create_time": event.create_time.strftime('%Y-%m-%d %H:%M'),
            "update_time": event.update_time.strftime('%Y-%m-%d %H:%M')
            }
            
    return HttpResponse('sending the info of [' + event.event_name + '] to your friend but currently not implemented!')
    
    
def applyYes(request):
    eventKey=request.POST.get('event_id')
    #return HttpResponse(str(eventKey))
    event=db.get(db.Key(eventKey))
    event.registered_count = event.registered_count + 1
    dicEventData={   "event_name": event.event_name,
                    "description": event.description,
                    "originator":event.originator,
                    "event_region": event.event_region,
                    "event_hours" : event.event_hours,
                    "event_target": event.event_target,
                    "event_field": event.event_field,
                    "create_time":event.create_time,
                    "category":event.category,
                    "start_time": event.start_time.strftime('%Y-%m-%d %H:%M'),
                    "end_time" : event.end_time.strftime('%Y-%m-%d %H:%M'),
                    "reg_start_time" : event.reg_start_time.strftime('%Y-%m-%d %H:%M'),
                    "reg_end_time": event.reg_end_time.strftime('%Y-%m-%d %H:%M'),
                    "objective": event.objective,
                    "summary":event.summary,
                    "event_id":event.event_id,
                    "expense": event.expense,
                    "registration_fee": event.registration_fee,
                    "registered_volunteer": event.registered_volunteer,
                    "registered_count": event.registered_count,
                    "approved_volunteer": event.approved_volunteer,
                    "approved_count": event.approved_count,
                    "status": event.status,
                    "approved": event.approved,
                    "approved_time": event.approved_time,
                    "attachment_links": event.attachment_links,
                    "tag": event.tag,
                    "max_age": event.max_age,
                    "min_age": event.min_age,
                    "sex": event.sex,
                    "female_req": event.female_req,
                    "male_req" : event.male_req,
                    "volunteer_req": event.volunteer_req,
                    "join_flow_plan": event.join_flow_plan,
                    "sentiments": event.sentiments,
                    "event_rating": event.event_rating,
                    "npo_event_rating": event.npo_event_rating,
                    "event_album_link": event.event_album_link,
                    "event_video_link": event.event_video_link,
                    "event_blog_link": event.event_blog_link,
                    "create_time": event.create_time.strftime('%Y-%m-%d %H:%M'),
                    "update_time": event.update_time.strftime('%Y-%m-%d %H:%M')
                    }
    userSet = db.GqlQuery('select * from VolunteerProfile')
    count = 0
    logging.info(userSet[0].volunteer_id)
    dicUserData={   "volunteer_id" : userSet[0].volunteer_id,
                    "id_no" : userSet[0].id_no,
                    "volunteer_last_name" : userSet[0].volunteer_last_name,
                    "volunteer_first_name" : userSet[0].volunteer_first_name,
                    "statue" : userSet[0].status
                }
 
    event.registered_volunteer.append(userSet[0].volunteer_id)
 
    now            = datetime.datetime.utcnow()
    volunteer_event_item = ddl.VolunteerEvent(
                                                volunteer_profile_ref=userSet[0], 
                                                event_profile_ref=event, 
                                                registered_time=now, 
                                                approved_time=now,
                                                status="new registration", 
                                                finished_event_hours=event.event_hours, 
                                                volunteer_event_rating=100, 
                                                event_rating=100,
                                                npo_event_rating=100
                                            )
    event.put()
    volunteer_event_item.put()
    return HttpResponse('Volunteer Event Data Added!')
                    
def applyNo(request):
    HttpResponse('Nothing was done!')
