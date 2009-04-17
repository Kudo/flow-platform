# coding=big5
import time, re ,urllib
from datetime import datetime
from django.http import HttpResponseRedirect,HttpResponseServerError,HttpResponseForbidden
from django.shortcuts import render_to_response
from google.appengine.ext import db
from google.appengine.api import users,memcache
from django import newforms as forms
from django.core import exceptions
from db import ddl
from google.appengine.ext.db import djangoforms
import flowBase,smsUtil

lstAcceptNumber=['0982197997']
    

def submitAuthToken(request,npoid):
    objUser,objVolunteer,objNpo=flowBase.verifyNpo(request,npoid)
    if not objNpo:
        raise RuntimeError('objNpo is None')

    if request.method=='GET':
        if 'event_key' not in request.GET:
            raise RuntimeError('event_key not defined')
        strEventKey=request.GET['event_key']
        dic={'event_key':strEventKey,
         'phone_number':request.GET.get('p',''),
         'base': flowBase.getBase(request, 'npo'),
         'page': 'event',
         'alertMsg':request.GET.get('m','')}
        if objVolunteer.cellphone_no and not dic['phone_number']:
            dic['phone_number']=''.join(objVolunteer.cellphone_no.split('-'))
        return render_to_response('event/event-sms-1.html', dic)
    
    if 'event_key' not in request.POST:
        raise RuntimeError('event_key not defined')
    strEventKey=request.POST['event_key']
    eventProfile=db.get(db.Key(strEventKey))
    if not eventProfile:
        raise RuntimeError('db key not found %s'%strEventKey)
    
    if eventProfile.npo_profile_ref.id!=objNpo.id:
        raise RuntimeError('NPO not match!')

    strPhoneNumber = request.POST['phone_number']
    if not strPhoneNumber.isdigit() or len(strPhoneNumber)!=10:
        dic={'m':u'手機號碼格式錯誤'.encode('utf-8'),'event_key':strEventKey,'p':strPhoneNumber}
        return HttpResponseRedirect('/npo/%s/admin/authEvent1?%s'%(npoid,urllib.urlencode(dic)))

    eventProfile.status = 'authenticating'
    strAuthToken=str(hash(str(time.time())))[-6:]
    strMemcacheKey='/submitAuthToken/%s'%strEventKey
    if not memcache.set(strMemcacheKey,strAuthToken,600):
        return HttpResponseServerError('call memcache.set() failed!')
    eventProfile.authenticate_retry_count+=1
    if eventProfile.authenticate_retry_count>=3:
        eventProfile.status = 'authenticating failed'
    if strPhoneNumber in lstAcceptNumber:
        smsUtil.sendSmsOnGAE(strPhoneNumber,u'[若水志工媒合平台] 活動驗證碼為:'+strAuthToken,objNpo.id,objVolunteer.id,eventProfile.id)

    eventProfile.put()
    dic={'event_key':strEventKey,'p':strPhoneNumber}
    return HttpResponseRedirect('/npo/%s/admin/authEvent3?%s'%(npoid,urllib.urlencode(dic)))

def handleEventAuth(request,npoid):
    objUser,objVolunteer,objNpo=flowBase.verifyNpo(request,npoid)
    if not objNpo:
        raise AssertionError("objNpo is None")

    if request.method=='GET':
        strEventKey=request.GET['event_key']
        strPhoneNumber=request.GET['p']
        strComment=''
        strMemcacheKey='/submitAuthToken/%s'%strEventKey
        if strPhoneNumber not in lstAcceptNumber:
            strToken=memcache.get(strMemcacheKey)
            strComment=u'簡訊驗證目前僅開放給 %s 使用，請直接輸入 %s 即可通過驗證'%(','.join(lstAcceptNumber),strToken)
        dic = {'debug_comment':strComment,
               'event_key':strEventKey,
               'base': flowBase.getBase(request,'npo'),
               'page':'event',
               }
        return render_to_response('event/event-sms-2.html', dic)
        
    if 'event_key' not in request.POST:
        raise RuntimeError('event_key not defined')
    strEventKey=request.POST['event_key']
    eventProfile=db.get(db.Key(strEventKey))
    if not eventProfile:
        raise RuntimeError('db key not found %s'%strEventKey)
    
    if eventProfile.npo_profile_ref.id!=objNpo.id:
        raise RuntimeError('NPO not match!')
    strMemcacheKey='/submitAuthToken/%s'%strEventKey
    strToken=memcache.get(strMemcacheKey)
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
    return HttpResponseRedirect('/npo/%s/admin/listEvent'%npoid)
    
