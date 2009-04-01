# -*- coding: big5 -*-
import logging,datetime
from django.http import HttpResponse
from google.appengine.api import mail
from google.appengine.ext import db
from db import ddl

def updateEventStatus():
    logging.debug('updateEventStatus')
    now=datetime.datetime.utcnow()
    results = db.GqlQuery("SELECT * FROM EventProfile WHERE status = :1 ",'approved').fetch(1000)
    for event in results:
        if now > event.reg_start_time:
            event.status='registrating'
            event.put()

    results = db.GqlQuery("SELECT * FROM EventProfile WHERE status = :1 ",'registrating').fetch(1000)
    for event in results:
        if now > event.reg_end_time:
            event.status='recruiting'
            event.put()

    results = db.GqlQuery("SELECT * FROM EventProfile WHERE status = :1 ",'recruiting').fetch(1000)
    for event in results:
        if now > event.start_time:
            event.status='on-going'
            event.put()

    results = db.GqlQuery("SELECT * FROM EventProfile WHERE status = :1 ",'on-going').fetch(1000)
    for event in results:
        if now > event.end_time:
            event.status='activity closed'
            event.put()

def every5minutes(request):
    #if request.META['REMOTE_ADDR']=='0.1.0.1':
    updateEventStatus()
    return HttpResponse('ok')

def hourly(request):
    logging.info('hourly cron test')
    return HttpResponse('ok')

def daily(request):
    logging.info('daily cron test')
    '''
    message = mail.EmailMessage()
    message.subject=u'若水志工媒合平台'
    message.sender = 'camgelo@gmail.com'
    message.to = 'chienchih_lo@trend.com.tw'
    message.body = u"""測試GAE的cron job! %s\r\n"""%(datetime.datetime.utcnow()+datetime.timedelta(hours=8))
    for event in ddl.EventProfile.gql('ORDER BY create_time DESC').fetch(100):
        message.body+='%s %s %s %s\r\n'%(event.event_name, event.npo_profile_ref.npo_name, event.create_time.strftime('%Y-%m-%d %H:%M'), event.description)
    message.send()
    '''
    return HttpResponse('ok')