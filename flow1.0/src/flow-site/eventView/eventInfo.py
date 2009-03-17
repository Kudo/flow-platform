#-*- coding: cp950 -*-
import sys,cgi,re,time,os,datetime
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import TemplateDoesNotExist
from django.http import HttpResponseRedirect
from google.appengine.ext import db
from google.appengine.api import users
from db import ddl
import flowBase

def showEvent(request):
    # Retrieve Events from Database
    eventKey=request.GET.get('id')
    event=db.get(db.Key(eventKey))
    if not event:
        return HttpResponseRedirect('/')
    intVolunteerNeeded = event.volunteer_req - event.approved_count
    dicData={'event': event,
             'event_key':event.key(),
             'base': flowBase.getBase(request, 'event'),
             'needed': str(intVolunteerNeeded)}
    return render_to_response(r'event/event-info.html',dicData)

def applyEvent(request):
    eventKey=request.POST.get('event_key')
    if not eventKey or eventKey=='None':
        return HttpResponseRedirect('/')
    event=db.get(db.Key(eventKey))
    if not event:
        return HttpResponseRedirect('/')

    objUser=users.get_current_user()
    if not objUser:
        return HttpResponseRedirect(users.create_login_url(cgi.escape(request.path+'?event_id=%s'%eventKey)))
    objVolunteer=flowBase.getVolunteer(objUser)
    if not objVolunteer:
        template_values = {
            'base': flowBase.getBase(request, 'event'),
            'redirectURI': cgi.escape(request.path+'?event_id=%s'%eventKey),
            'loginSuccess': False,
        }
        return render_to_response('loginProxy.html', template_values)
    
    intVolunteerEventItems = db.GqlQuery('select * from VolunteerEvent where volunteer_profile_ref = :1 and event_profile_ref = :2', objVolunteer, event).count()
    if intVolunteerEventItems > 0:
        strAlert=u'此活動您已經報名了'
    else:
        event.registerUser(objVolunteer)
        strAlert=u'報名成功 '

    dicData={'event': event,
             'event_key':event.key(),
             'base': flowBase.getBase(request, 'event'),
             'needed': str(event.volunteer_req - event.approved_count),
             'alertMsg':strAlert}
    return render_to_response(r'event/event-info.html',dicData)
                    

def EmptyApply(request):
    eventKey=request.POST.get('event_id')
    #return HttpResponse(str(eventKey))
    EventProfile = db.GqlQuery('select * from EventProfile')
    for event in EventProfile:
        event.registered_count=0
        #event.registered_volunteer=[]
        event.put()

    VolunteerEvent = db.GqlQuery("select * from VolunteerEvent")
    for item in VolunteerEvent:
        item.delete()
    return HttpResponse(u'已刪除VolunteerEvent所有資料,與清除EventProfile相對應欄位')

