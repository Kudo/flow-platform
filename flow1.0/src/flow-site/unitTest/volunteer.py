#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import datetime
from db.ddl import *
from google.appengine.api import users
from django.http import HttpResponse

def create(request):
    response = HttpResponse(mimetype="text/plain; charset=utf-8")
    now       = datetime.datetime.utcnow()
    try:
        user = users.User("ckchien@gmail.com")
        kudo = VolunteerProfile(volunteer_id=user, id_no="M123456789", volunteer_last_name="Chien", volunteer_first_name="Kudo", gmail=user.email(),
                                     date_birth=datetime.date(1984, 6, 2), expertise=[u"家政"], sex="Male", phone_no="02-1234-5678", resident_country=u"中華民國",
                                     resident_postal="104", resident_state=u"台灣省", resident_city=u"臺北縣市", resident_district=u"大安區",
                                     prefer_region=[u'臺北', u'台中'], prefer_zip=[u'104'], prefer_target=[u'老弱婦孺'], prefer_field=[u'聊天'], prefer_group=[u'不拘'],
                                     create_time=now, update_time=now, volunteer_rating=80, status="normal", search_text="Kudo in the house",
                                     valid_google_acct=True, cellphone_no='0912-345-678', tag=['Kudo', u'測試'], organization='Consumer',
                                     blog='http://www.kudo.idv.tw/blog/', brief_intro='Nobody', logo='http://farm4.static.flickr.com/3238/3042955911_f0730a2640.jpg',
                                     total_serv_hours=20, total_reg_events=5, total_serv_events=6,
                                     )

        user = users.User("gina@gmail.com")
        gina = VolunteerProfile(volunteer_id=user, id_no="M123456789", volunteer_last_name="Lin", volunteer_first_name="Gina", gmail=user.email(),
                                     date_birth=datetime.date(1984, 6, 2), expertise=[u"護理", u"中國文學"], sex="Female", phone_no="02-1234-5678", resident_country=u"中華民國",
                                     resident_postal="104", resident_state=u"台灣省", resident_city=u"臺北縣市", resident_district=u"大安區",
                                     prefer_region=[u'臺北', u'台中'], prefer_zip=[u'104'], prefer_target=[u'老弱婦孺'], prefer_field=[u'聊天'], prefer_group=[u'不拘'],
                                     create_time=now, update_time=now, volunteer_rating=80, status="normal", search_text="Gina in the house",
                                     valid_google_acct=True, cellphone_no='0912-345-678', tag=['gina', u'美女'], organization='Consumer',
                                     blog='http://www.kudo.idv.tw/blog/', brief_intro='Dear', logo='http://farm1.static.flickr.com/130/330862184_bd33d077d6.jpg',
                                     total_serv_hours=20, total_reg_events=5, total_serv_events=6,
                                     )

        user = users.User("root@gmail.com")
        root = VolunteerProfile(volunteer_id=user, id_no="M123456789", volunteer_last_name="Root", volunteer_first_name="Charlie", gmail=user.email(),
                                     date_birth=datetime.date(1984, 6, 2), expertise=[u"資訊"], sex="Male", phone_no="02-1234-5678", resident_country=u"中華民國",
                                     resident_postal="104", resident_state=u"台灣省", resident_city=u"臺北縣市", resident_district=u"大安區",
                                     prefer_region=[u'臺北', u'台中'], prefer_zip=[u'104'], prefer_target=[u'老弱婦孺'], prefer_field=[u'聊天'], prefer_group=[u'不拘'],
                                     create_time=now, update_time=now, volunteer_rating=80, status="normal", search_text="神秘嘉賓",
                                     valid_google_acct=True, cellphone_no='0912-345-678', tag=['root'], organization='Consumer',
                                     blog='http://www.kudo.idv.tw/blog/', brief_intro='root',
                                     total_serv_hours=20, total_reg_events=5, total_serv_events=6,
                                     )

        kudoRef = kudo.put()
        ginaRef = gina.put()
        rootRef = root.put()
        kudo.friends = [ginaRef, rootRef]
        gina.friends = [kudoRef]
        kudo.volunteer_profile = [ginaRef]
        gina.volunteer_profile = [kudoRef]
        
        kudo.put()
        gina.put()
    except:
        response.write('新增 VolunteerProfile 失敗 (%s)' % str(sys.exc_info()))
        return response

    response.write('新增 VolunteerProfile 成功!!!')
    return response

def bulkCreate(request):
    response = HttpResponse(mimetype="text/plain; charset=utf-8")
    now       = datetime.datetime.utcnow()
    try:
        for i in range(0, 100):
            user = users.User("ckchien" + str(i) + "@gmail.com")
            volunteer = VolunteerProfile(volunteer_id=user, id_no="M123456789", volunteer_last_name="Chien", volunteer_first_name="Kudo", gmail=user.email(),
                                         date_birth=datetime.date(1984, 6, 2), expertise=[u"資訊"], sex="Male", phone_no="02-1234-5678", resident_country=u"中華民國",
                                         resident_postal="104", resident_state=u"台灣省", resident_city=u"臺北縣市", resident_district=u"大安區",
                                         prefer_region=[u'臺北', u'台中'], prefer_zip=[u'104'], prefer_target=[u'老弱婦孺'], prefer_field=[u'聊天'], prefer_group=[u'不拘'],
                                         create_time=now, update_time=now, volunteer_rating=80, status="normal", search_text="Kudo in the house",
                                         valid_google_acct=True, cellphone_no='0912-345-678', tag=['Kudo', u'測試'], organization='Consumer',
                                         blog='http://www.kudo.idv.tw/blog/', brief_intro='Nobody', logo='http://farm4.static.flickr.com/3238/3042955911_f0730a2640.jpg',
                                         total_serv_hours=20, total_reg_events=5, total_serv_events=6,
                                         )

            volunteer.put()
    except:
        response.write('大量新增 VolunteerProfile 失敗 (%s)' % str(sys.exc_info()))
        return response

    response.write('大量新增 VolunteerProfile 成功!!!')
    return response
