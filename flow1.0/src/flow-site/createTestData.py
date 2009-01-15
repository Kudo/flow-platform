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

from db import ddl3

def createNpoProfile():
    user = users.User("trend@flow.org",'local')
    now  = datetime.datetime.utcnow()
    npo  = ddl3.NpoProfile(npo_name='kids', founder="John Doe", google_acct=user, country='ROC', postal="104", state='TW', city='tp',
                      district='NK', founding_date=datetime.date(1980, 1, 1), authority="GOV", tag=["wild lives", "marines"],
                      status="new application", docs_link=["Timbuck2"], npo_rating=1, create_time=now, update_time=now)
    npo.put()
    return npo

def createVolunteerProfile():
    user      = users.User("trend@flow.org",'local')
    now       = datetime.datetime.utcnow()
    volunteer = ddl3.VolunteerProfile(volunteer_id=user, id_no="A123456789", volunteer_last_name="Doe", volunteer_first_name="Jane", gmail=user.email(),
                                 date_birth=datetime.date(1970, 2, 1), expertise=['eat','drink','gambling'], sex="Female", phone_no="02-1234-5678", resident_country="ROC",
                                 resident_postal="104", resident_state='tw', resident_city='tp', resident_district='SL',
                                 prefer_region=['taipei'], prefer_zip=['106'], prefer_target=['test'], prefer_field=['drive'], prefer_group=['trend'],
                                 create_time=now, update_time=now, volunteer_rating=80, status="normal")

    volunteer.put()
    return volunteer
    
def createQuestionnaireTemplate():
    now      = datetime.datetime.utcnow()
    template = ddl3.QuestionnaireTemplate(questions_xml="<Question>Howdy</Question>", create_time=now, status="Normal")
    template.put()
    return template

def createEventProfile(npo, volunteer, template):
    now   = datetime.datetime.utcnow()
    start = datetime.datetime.utcfromtimestamp(time.time()+86400*10)
    end = datetime.datetime.utcfromtimestamp(time.time()+86400*15)
    event = ddl3.EventProfile(event_id=str(int(time.time())), event_name=u'大家一起做網頁', description='sea', npo_profile_ref=npo,
                         volunteer_profile_ref=volunteer, event_region=[u'南投'], event_zip=["104"], event_hours=10,
                         event_target=['social worker'], event_field=['social activity'], category='Social',
                         start_time=start, end_time=end, reg_start_time=start, reg_end_time=end, objective='orcas',
                         status="approved", max_age=99, min_age=9, questionnaire_template_ref=template, event_rating=75, npo_event_rating=80,
                         create_time=now, update_time=now, summary='Good Job!',volunteer_req=10)

    event.put()
    return event

def createEventProfile2(npo, volunteer, template, strEvent_id, strEvent_name, strStatus):
    #startUnitTest("EventProfile.unitTest")

    now = datetime.datetime.utcnow()
    start = datetime.datetime.utcfromtimestamp(time.time()+86400*10)
    end = datetime.datetime.utcfromtimestamp(time.time()+86400*15)
    event = ddl3.EventProfile(event_id=strEvent_id, event_name=strEvent_name, description=u'測試', npo_profile_ref=npo,
                         volunteer_profile_ref=volunteer, event_region=['Taipei'], event_zip=["104"], event_hours=10,
                         event_target=['social worker'], event_field=['social activity'], category='Social',
                         start_time=start, end_time=end, reg_start_time=start, reg_end_time=end, objective='orcas',
                         status=strStatus, max_age=99, min_age=9, questionnaire_template_ref=template, event_rating=75, npo_event_rating=80,
                         create_time=now, update_time=now, summary='Good Job!',volunteer_req=5)

    event.put()
    return event

def setupDevServerEnv():
    import os
    #os.environ['APPLICATION_ID']='flow'
    from google.appengine.tools import dev_appserver,dev_appserver_main
    config, matcher = dev_appserver.LoadAppConfig('', {})
    option_dict = dev_appserver_main.DEFAULT_ARGS.copy()
    dev_appserver.SetupStubs(config.application, **option_dict)
    
def main():
    setupDevServerEnv()
    npo = createNpoProfile()
    volunteer = createVolunteerProfile()
    template = createQuestionnaireTemplate()
    event = createEventProfile(npo, volunteer, template)
    event = createEventProfile2(npo, volunteer, template, str(int(time.time())), u"招募中的活動", "recruiting" )
    event = createEventProfile2(npo, volunteer, template, str(int(time.time())), "TestEvent2", "activity closed" )
    event = createEventProfile2(npo, volunteer, template, str(int(time.time())), "TestEvent3", "activity closed" )
    event = createEventProfile2(npo, volunteer, template, str(int(time.time())), "TestEvent4", "activity closed" )
    event = createEventProfile2(npo, volunteer, template, str(int(time.time())), "TestEvent5", "activity closed" )
    
if __name__=='__main__':
    main()
