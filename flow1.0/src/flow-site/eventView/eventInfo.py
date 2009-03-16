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
    intVolunteerNeeded = event.volunteer_req - event.approved_count
    dicData={'event' : event,
             'base': flowBase.getBase(request, 'event'),
             'needed': str(intVolunteerNeeded),
             'event_key': str(eventKey)}
    return render_to_response(r'event/event-apply.html', dicData)

def mailToFriend(request):
    eventKey=request.POST.get('event_key')
    #return HttpResponse(str(eventKey))
    event=db.get(db.Key(eventKey))
    return HttpResponse(u'���\��N�|�⬡�� [' + event.event_name + u'] ����T�o�H���A���B��,���O�ثe�٨S���ظm!')
    
def applyYes(request):
    # choose I want to apply , there will be:
    # (1) trying select whether current user existed in VolunteerEvent table, if existed will return some information
    # (2) if not existed, then add the use, and then add registered_count 1, and registered_volunteer list will be added as well.
    eventKey=request.POST.get('event_key')
    if not eventKey or eventKey=='None':
        return HttpResponseRedirect('/')
    event=db.get(db.Key(eventKey))
    if not event:
        return HttpResponseRedirect('/')
    objVolunteer=flowBase.getVolunteer()
    if not objVolunteer:
        return HttpResponseRedirect('/')
    
    intVolunteerEventItems = db.GqlQuery('select * from VolunteerEvent where volunteer_profile_ref = :1 and event_profile_ref = :2', objVolunteer, event).count()
    if intVolunteerEventItems > 0:
        return HttpResponse(u'���b�� %s �w�g�����W[%s]�F,�ҥH�L�k�A�[�J!<br><a href="/event/">��^</a>' % (objVolunteer.volunteer_id,event.event_name) )
        
    event.registerUser(objVolunteer)
    return HttpResponse(u'�Ӥu [%s] �w���W [%s] ���\!<br><a href="/event/">��^</a>' % (objVolunteer.volunteer_id, event.event_name))
                    
def applyNo(request):
    return HttpResponseRedirect('/event/')

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
    return HttpResponse(u'�w�R��VolunteerEvent�Ҧ����,�P�M��EventProfile�۹������')

