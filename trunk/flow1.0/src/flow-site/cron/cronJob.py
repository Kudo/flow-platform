# -*- coding: big5 -*-
import logging,datetime
from django.http import HttpResponse
from google.appengine.api import mail
from google.appengine.ext import db
from db import ddl

def updateEventStatus():
    now=datetime.datetime.utcnow()
    results = db.GqlQuery("SELECT * FROM EventProfile WHERE status = :1 ",'approved').fetch(1000)
    for event in results:
        if now >= event.reg_start_time:
            event.status='registrating'
            event.put()

    results = db.GqlQuery("SELECT * FROM EventProfile WHERE status = :1 ",'registrating').fetch(1000)
    for event in results:
        if now >= event.reg_end_time:
            event.status='registration closed'
            event.put()

    results = db.GqlQuery("SELECT * FROM EventProfile WHERE status = :1 ",'registration closed').fetch(1000)
    for event in results:
        if now >= event.start_time:
            event.status='on-going'
            event.put()

    results = db.GqlQuery("SELECT * FROM EventProfile WHERE status = :1 ",'on-going').fetch(1000)
    for event in results:
        if now >= event.end_time:
            event.status='activity closed'
            event.put()
            try:
                event.npo_profile_ref.total_events+=1
                event.npo_profile_ref.put()
            except:
                logging.error('Update event.npo_profile_ref.total_events failed! event_id=%s'%event.event_id)

def every5minutes(request):
    #if request.META['REMOTE_ADDR']=='0.1.0.1':
    updateEventStatus()
    return HttpResponse('ok')

def hourly(request):
    #logging.info('hourly cron test')
    return HttpResponse('ok')

def daily(request):
    return HttpResponse('ok')