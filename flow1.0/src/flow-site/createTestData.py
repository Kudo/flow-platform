# -*- coding: cp950 -*-

import sys,datetime,cgi,re,time,os

DIR_PATH = r'c:\Program Files\Google\google_appengine'
EXTRA_PATHS = [
  DIR_PATH,
  os.path.join(DIR_PATH, 'lib', 'django'),
  os.path.join(DIR_PATH, 'lib', 'webob'),
  os.path.join(DIR_PATH, 'lib', 'yaml', 'lib'),
]
sys.path = EXTRA_PATHS + sys.path

from google.appengine.api import users
from db import ddl

def createNpoProfile(user):
    now  = datetime.datetime.now()
    npo  = ddl.NpoProfile(npo_name=u'宅男激金會', founder="John Doe", google_acct=user, country='ROC', postal="104", state='TW', city=u'臺北縣市',
                      district='NK', founding_date=datetime.date(1980, 1, 1), authority="GOV", tag=["wild lives", "marines"],
                      status="new application", docs_link=["Timbuck2"], npo_rating=1, create_time=now, update_time=now)
    npo.put()
    return npo

def createVolunteerProfile(user):
    now       = datetime.datetime.now()
    volunteer = ddl.VolunteerProfile(key_name=str(user), volunteer_id=user, id_no="A123456789", volunteer_last_name=u"林", volunteer_first_name=u"志玲", gmail=user.email(),
                                 date_birth=datetime.date(1970, 2, 1), expertise=['eat','drink','gambling'], sex="Female", phone_no="02-1234-5678",cellphone_no="0982-197-997", resident_country="ROC",
                                 resident_postal="104", resident_state='tw', resident_city=u'臺北縣市', resident_district='SL',
                                 prefer_region=['taipei'], prefer_zip=['106'], prefer_target=['test'], prefer_field=['drive'], prefer_group=['trend'],
                                 create_time=now, update_time=now, volunteer_rating=80, status="normal",nickname='trend')
    volunteer.put()
    return volunteer

def createVolunteerProfile1():
    user      = users.User("camge@flow.org",'local')
    now       = datetime.datetime.now()
    volunteer = ddl.VolunteerProfile(key_name=str(user), volunteer_id=user, id_no="Q123456789", volunteer_last_name=u"羅", volunteer_first_name=u"健志", gmail=user.email(),
                                 date_birth=datetime.date(1980, 2, 1), expertise=['eat','drink','gambling'], sex="Male", phone_no="02-1234-5678",cellphone_no="0982-000-997", resident_country="ROC",
                                 resident_postal="104", resident_state='tw', resident_city=u'臺北縣市', resident_district='SL',
                                 prefer_region=['taipei'], prefer_zip=['106'], prefer_target=['test'], prefer_field=['drive'], prefer_group=['trend'],
                                 create_time=now, update_time=now, volunteer_rating=80, status="normal",nickname='camge')
    volunteer.put()
    return volunteer
    
def createQuestionnaireTemplate():
    now      = datetime.datetime.now()
    template = ddl.QuestionnaireTemplate(questions_xml="<Question>Howdy</Question>", create_time=now, status="Normal")
    template.put()
    return template

def createEventProfile(npo, volunteer):
    now   = datetime.datetime.now()
    start = datetime.datetime.fromtimestamp(time.time()+86400*10)
    end = datetime.datetime.fromtimestamp(time.time()+86400*11)
    reg_start=now
    reg_end=datetime.datetime.fromtimestamp(time.time()+86400*5)
    event = ddl.EventProfile(event_name=u'大家一起做網頁', description='sea', npo_profile_ref=npo,
                         volunteer_profile_ref=volunteer, event_region=[u'臺北縣市'], event_hours=10,
                         start_time=start, end_time=end, reg_start_time=reg_start, reg_end_time=reg_end, objective='orcas',
                         status="approved", max_age=99, min_age=9, event_rating=75, npo_event_rating=80,
                         create_time=now, update_time=now, summary='Good Job!',volunteer_req=10,tag=[u'網頁'])
    event.approved=True
    event.approved_time=datetime.datetime.now()
    event.put()
    return event

def createEventProfile2(npo, volunteer, strEvent_name, strStatus):
    if strStatus=='activity closed':
        now = datetime.datetime.fromtimestamp(time.time()-86400*20)
        start = datetime.datetime.fromtimestamp(time.time()-86400*15)
        end = datetime.datetime.fromtimestamp(time.time()-86400*10)
    else:
        now   = datetime.datetime.now()
        start = datetime.datetime.fromtimestamp(time.time()+86400*10)
        end = datetime.datetime.fromtimestamp(time.time()+86400*15)
        
    event = ddl.EventProfile(event_name=strEvent_name, description=u'測試', npo_profile_ref=npo,
                         volunteer_profile_ref=volunteer, event_region=['Taipei'], event_hours=10,
                         start_time=start, end_time=end, reg_start_time=now, reg_end_time=start, objective='orcas',
                         status=strStatus, max_age=99, min_age=9, event_rating=75, npo_event_rating=80,
                         create_time=now, update_time=now, summary='Good Job!',volunteer_req=5,tag=[u'測試'])
    if strStatus!="new application":
        event.approved=True
        event.approved_time=datetime.datetime.fromtimestamp(time.time()-86400*19)
    event.put()
    return event

def setupDevServerEnv():
    import os
    #os.environ['APPLICATION_ID']='flow'
    from google.appengine.tools import dev_appserver,dev_appserver_main
    config, matcher = dev_appserver.LoadAppConfig('', {})
    option_dict = dev_appserver_main.DEFAULT_ARGS.copy()
    dev_appserver.SetupStubs(config.application, **option_dict)
    

def create():
    createVolunteerProfile1()
    
    user = users.User("trend@flow.org",'local')
    volunteer = createVolunteerProfile(user)
    npo = createNpoProfile(user)
    
    event = createEventProfile(npo, volunteer)
    event = createEventProfile2(npo, volunteer, u"招募中的活動", "recruiting" )
    event = createEventProfile2(npo, volunteer, u"蓋高速公路", "new application" )
    event = createEventProfile2(npo, volunteer, u"打螞蟻", "activity closed" )
    event = createEventProfile2(npo, volunteer, u"殺蟑螂", "activity closed" )
    event = createEventProfile2(npo, volunteer, u"毒老鼠", "activity closed" )
    
def createFromGae(request):
    from django.http import HttpResponse
    create()
    return HttpResponse('done')

def main():
    setupDevServerEnv()
    create()
    return

if __name__=='__main__':
    main()
