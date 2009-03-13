# coding=big5
import time, re
from datetime import datetime
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from google.appengine.ext import db
from google.appengine.api import users,memcache
from django import newforms as forms
from db import ddl
from google.appengine.ext.db import djangoforms
import flowBase,smsUtil

def submitAuthToken(request):
    objUser=users.get_current_user()
    if not objUser:
        return HttpResponseRedirect('/')
    objVolunteer=flowBase.getVolunteer(objUser)
    if not objVolunteer:
        return HttpResponseRedirect('/')
    objNpo=flowBase.getNpoByUser(objUser)
    if not objNpo:
        return HttpResponseRedirect('/')
    
    if request.method != 'POST':
        return HttpResponseRedirect('/')
    
    eventKey=request.POST.get('event_key')
    if not eventKey:
        return HttpResponseRedirect('/')
    strPhoneNumber = request.POST['phone_number']
    eventProfile=db.get(db.Key(eventKey))
    if None == eventProfile:
        raise db.BadQueryError()
    eventProfile.status = 'authenticating'
    eventProfile.put()
    strToken=str(hash(str(time.time())))[-6:]
    if not memcache.set(str(eventProfile.key()),strToken,3600):
        raise RuntimeError('call memcache.set failed!')
    # We should unmark this line after release
    #smsUtil.sendSmsOnGAE(strPhoneNumber,u'您的驗證碼為:'+strToken)
    dic = {'auth_token':strToken,
           'event_key':eventKey,
           'base': flowBase.getBase(request,'npo'),
           'page':'event',
           }
    return render_to_response('event/event-sms-2.html', dic)

def handleEventAuth(request):
    objUser=users.get_current_user()
    if not objUser:
        return HttpResponseRedirect('/')
    objVolunteer=flowBase.getVolunteer(objUser)
    if not objVolunteer:
        return HttpResponseRedirect('/')
    objNpo=flowBase.getNpoByUser(objUser)
    if not objNpo:
        return HttpResponseRedirect('/')
    if request.method != 'POST':
        return HttpResponseRedirect('/')
    eventKey=request.POST.get('event_key')
    if not eventKey:
        return HttpResponseRedirect('/')

    eventProfile=db.get(db.Key(eventKey))
    if None == eventProfile:
        raise db.BadQueryError()
    strToken=memcache.get(eventKey)
    if strToken==request.POST['validation']:
        eventProfile.status = 'authenticated'
        eventProfile.put()
    else:
        dic={'token_invalid':'1',
             'auth_token':strToken,
             'event_key':eventKey,
             'base': flowBase.getBase(request,'npo'),
             'page':'event'}
        return render_to_response('event/event-sms-2.html', dic)
    return HttpResponseRedirect('.')
    
