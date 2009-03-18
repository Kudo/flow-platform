# coding=big5
import time, re ,urllib
from datetime import datetime
from django.http import HttpResponseRedirect,HttpResponseServerError,HttpResponseForbidden
from django.shortcuts import render_to_response
from google.appengine.ext import db
from google.appengine.api import users,memcache
from django import newforms as forms
from db import ddl
from google.appengine.ext.db import djangoforms
import flowBase,smsUtil

lstAcceptNumber=['0982197997']
    

def submitAuthToken(request):
    objUser,objVolunteer,objNpo=flowBase.verifyNpo(request)
    if not objNpo:
        return HttpResponseForbidden(u'錯誤的操作流程')

    if request.method=='GET':
        if 'event_key' not in request.GET:
            return HttpResponseForbidden(u'錯誤的操作流程')
        strEventKey=request.GET['event_key']
        dic={'event_key':strEventKey,
         'phone_number':request.GET.get('p') or ''.join(objVolunteer.cellphone_no.split('-')),
         'base': flowBase.getBase(request, 'npo'),
         'page': 'event',
         'alertMsg':request.GET.get('m','')}
        return render_to_response('event/event-sms-1.html', dic)
    
    if 'event_key' not in request.POST:
        return HttpResponseForbidden(u'錯誤的操作流程')
    strEventKey=request.POST['event_key']
    eventProfile=db.get(db.Key(strEventKey))
    if not eventProfile:
        return HttpResponseForbidden(u'錯誤的操作流程')
    
    if eventProfile.npo_profile_ref.id!=objNpo.id:
        return HttpResponseForbidden(u'錯誤的操作流程')

    strPhoneNumber = request.POST['phone_number']
    if not strPhoneNumber.isdigit() or len(strPhoneNumber)!=10:
        dic={'m':u'手機格式錯誤','event_key':strEventKey,'p':strPhoneNumber}
        return HttpResponseRedirect('authEvent1?%s'%(urllib.urlencode(dic)))

    eventProfile.status = 'authenticating'
    eventProfile.put()
    if not memcache.get(strEventKey):
        strAuthToken=str(hash(str(time.time())))[-6:]
        if not memcache.set(strEventKey,strAuthToken,1800):
            return HttpResponseServerError('call memcache.set() failed!')
        if strPhoneNumber in lstAcceptNumber:
            smsUtil.sendSmsOnGAE(strPhoneNumber,u'您的驗證碼為:'+strAuthToken)
    else:
        strAuthToken=memcache.get(strEventKey)
    dic={'event_key':strEventKey,'p':strPhoneNumber}
    return HttpResponseRedirect('authEvent3?%s'%(urllib.urlencode(dic)))

def handleEventAuth(request):
    objUser,objVolunteer,objNpo=flowBase.verifyNpo(request)
    if not objNpo:
        return HttpResponseForbidden(u'錯誤的操作流程')

    if request.method=='GET':
        strEventKey=request.GET['event_key']
        strPhoneNumber=request.GET['p']
        strComment=''
        if strPhoneNumber not in lstAcceptNumber:
            strToken=memcache.get(strEventKey)
            strComment=u'簡訊驗證目前僅開放給 %s 使用，請直接輸入 %s 即可通過驗證'%(','.join(lstAcceptNumber),strToken)
        dic = {'debug_comment':strComment,
               'event_key':strEventKey,
               'base': flowBase.getBase(request,'npo'),
               'page':'event',
               }
        return render_to_response('event/event-sms-2.html', dic)
        
    if 'event_key' not in request.POST:
        return HttpResponseForbidden(u'錯誤的操作流程')
    strEventKey=request.POST['event_key']
    eventProfile=db.get(db.Key(strEventKey))
    if not eventProfile:
        return HttpResponseForbidden(u'錯誤的操作流程')
    
    if eventProfile.npo_profile_ref.id!=objNpo.id:
        return HttpResponseForbidden(u'錯誤的操作流程')

    strToken=memcache.get(strEventKey)
    if strToken and strToken==request.POST['validation']:
        #eventProfile.status = 'authenticated'
        eventProfile.status = 'approved'
        eventProfile.put()
    else:
        dic={'token_invalid':'1',
             'validation':request.POST['validation'],
             'debug_comment':request.POST.get('debug_comment',''),
             'event_key':strEventKey,
             'base': flowBase.getBase(request,'npo'),
             'page':'event'}
        return render_to_response('event/event-sms-2.html', dic)
    return HttpResponseRedirect('/npo/admin/listEvent')
    
