#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import time
import datetime
from db.ddl import *
from google.appengine.api import users
from django.http import HttpResponse

def createNpoProfile():
    user = users.User("ckchien@gmail.com")
    now  = datetime.datetime.now()
    npo  = NpoProfile(npo_name=u'宅男激金會', founder="John Doe", google_acct=user, country='ROC', postal="104", state='TW', city='tp',
                      district='NK', founding_date=datetime.date(1980, 1, 1), authority="GOV", tag=["wild lives", "marines"],
                      status="new application", docs_link=["Timbuck2"], npo_rating=1, create_time=now, update_time=now,
                      brief_intro=u"簡單測試過長文字，應該要處理這個情形")
    npo.put()
    return npo

def createVolunteerProfile():
    now = datetime.datetime.now()
    user = users.User("ckchien@gmail.com")
    volunteer = VolunteerProfile(key_name=str(user), volunteer_id=user, nickname=user.nickname(), id_no="M123456789", volunteer_last_name="Chien", volunteer_first_name="Kudo", gmail=user.email(),
                                 date_birth=datetime.date(1984, 6, 2), expertise=[u"Nothing"], sex="Male", phone_no="02-1234-5678", resident_country=u"中華民國",
                                 resident_postal="104", resident_state=u"台灣省", resident_city=u"臺北縣市", resident_district=u"大安區",
                                 prefer_region=[u'臺北', u'台中'], prefer_zip=[u'104'], prefer_target=[u'老弱婦孺'], prefer_field=[u'聊天'], prefer_group=[u'不拘'],
                                 create_time=now, update_time=now, volunteer_rating=80, status="normal", search_text="Kudo in the house",
                                 valid_google_acct=True, cellphone_no='0912-345-678', tag=['Kudo', u'測試'], organization='Consumer',
                                 blog='http://www.kudo.idv.tw/blog/', brief_intro='Nobody', logo='http://farm4.static.flickr.com/3238/3042955911_f0730a2640.jpg',
                                 total_serv_hours=20, total_reg_events=5, total_serv_events=6,
                                 )
    volunteer.put()
    return volunteer
    
def createQuestionnaireTemplate():
    now      = datetime.datetime.now()
    template = QuestionnaireTemplate(questions_xml="<Question>Howdy</Question>", create_time=now, status="Normal")
    template.put()
    return template

def createEventProfile(npo, volunteer, template):
    now   = datetime.datetime.now()
    start = datetime.datetime.fromtimestamp(time.time()+86400*10)
    end = datetime.datetime.fromtimestamp(time.time()+86400*15)
    event = EventProfile(event_id=str(int(time.time())), event_name=u'大家一起做網頁', description='sea', npo_profile_ref=npo,
                         volunteer_profile_ref=volunteer, event_region=[u'南投'], event_zip=["104"], event_hours=10,
                         event_target=['social worker'], event_field=['social activity'], category='Social',
                         start_time=start, end_time=end, reg_start_time=start, reg_end_time=end, objective='orcas',
                         status="approved", max_age=99, min_age=9, questionnaire_template_ref=template, event_rating=75, npo_event_rating=80,
                         create_time=now, update_time=now, summary='Good Job!',volunteer_req=10)
    event.approved=True
    event.approved_time=datetime.datetime.now()
    event.put()
    return event

def createEventProfile2(npo, volunteer, template, strEvent_id, strEvent_name, strStatus):
    if strStatus=='activity closed':
        now = datetime.datetime.fromtimestamp(time.time()-86400*20)
        start = datetime.datetime.fromtimestamp(time.time()-86400*15)
        end = datetime.datetime.fromtimestamp(time.time()-86400*10)
    else:
        now   = datetime.datetime.now()
        start = datetime.datetime.fromtimestamp(time.time()+86400*10)
        end = datetime.datetime.fromtimestamp(time.time()+86400*15)
        
    event = EventProfile(event_id=strEvent_id, event_name=strEvent_name, description=u'測試', npo_profile_ref=npo,
                         volunteer_profile_ref=volunteer, event_region=['Taipei'], event_zip=["104"], event_hours=10,
                         event_target=['social worker'], event_field=['social activity'], category='Social',
                         start_time=start, end_time=end, reg_start_time=start, reg_end_time=end, objective='orcas',
                         status=strStatus, max_age=99, min_age=9, questionnaire_template_ref=template, event_rating=75, npo_event_rating=80,
                         create_time=now, update_time=now, summary='Good Job!',volunteer_req=5)
    event.approved=True
    event.approved_time=datetime.datetime.fromtimestamp(time.time()-86400*19)
    event.put()
    return event

def create(request):
    response = HttpResponse(mimetype="text/plain; charset=utf-8")
    try:
        volunteer = createVolunteerProfile()
        npo = createNpoProfile()
        volunteer.npo_profile_ref = [npo.key()]
        volunteer.put()
        npo.members = [volunteer.key()]
        npo.put()
        template = createQuestionnaireTemplate()
        event = createEventProfile(npo, volunteer, template)
        event = createEventProfile2(npo, volunteer, template, str(int(time.time())), u"招募中的活動", "recruiting" )
        event = createEventProfile2(npo, volunteer, template, str(int(time.time())), u"蓋高速公路", "activity closed" )
        event = createEventProfile2(npo, volunteer, template, str(int(time.time())), u"打螞蟻", "activity closed" )
        event = createEventProfile2(npo, volunteer, template, str(int(time.time())), u"殺蟑螂", "activity closed" )
        event = createEventProfile2(npo, volunteer, template, str(int(time.time())), u"毒老鼠", "activity closed" )
    except:
        response.write('新增失敗 (%s)' % str(sys.exc_info()))
        return response

    response.write('新增成功!!!')
    return response
