# -*- coding: big5 -*-
import logging,datetime
from django.http import HttpResponse
from google.appengine.api import mail
from db import ddl

def every5minutes(request):
    logging.info('every5minutes cron test')
    return HttpResponse('ok')

def hourly(request):
    logging.info('hourly cron test')
    return HttpResponse('ok')

def daily(request):
    logging.info('daily cron test')
    message = mail.EmailMessage()
    message.subject=u'若水志工媒合平台'
    message.sender = 'camgelo@gmail.com'
    message.to = 'chienchih_lo@trend.com.tw'
    message.body = u"""測試GAE的cron job! %s\r\n"""%(datetime.datetime.utcnow()+datetime.timedelta(hours=8))
    for event in ddl.EventProfile.gql('ORDER BY create_time DESC').fetch(100):
        message.body+='%s %s %s %s\r\n'%(event.event_name, event.npo_profile_ref.npo_name, event.create_time.strftime('%Y-%m-%d %H:%M'), event.description)
    message.send()
    
    return HttpResponse('ok')