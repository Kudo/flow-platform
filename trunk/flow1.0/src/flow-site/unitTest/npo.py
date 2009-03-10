#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import time
import datetime
from db.ddl import *
from google.appengine.api import users
from django.http import HttpResponse

def create(request):
    response = HttpResponse(mimetype="text/plain; charset=utf-8")
    now       = datetime.datetime.utcnow()
    try:
        user = users.User("ckchien@gmail.com")
        volunteer = VolunteerProfile.all().filter('volunteer_id = ', user).get()
        if not volunteer:
            return
        npo  = NpoProfile(npo_name=u"若水國際", founder=u"張明正 & 王文華", google_acct=user, country=u"ROC", postal=u"104", state=u"Taiwan", city=u"Taipei",
                district=u"大安區", founding_date=datetime.date(2007, 6, 1), authority=u"GOV", tag=[u"flow"],
                status=u"new application", docs_link=[u"Timbuck2"], npo_rating=1, create_time=now, update_time=now)
        npo.members = [volunteer.key()]
        npo.put()
        volunteer.npo_profile_ref = [npo.key()]
        volunteer.put()
    except:
        response.write('新增 NpoProfile 失敗!!!')
        return response

    response.write('新增 NpoProfile 成功!!!')
    return response

def bulkCreate(request):
    response = HttpResponse(mimetype="text/plain; charset=utf-8")
    user = users.User("ckchien@gmail.com")
    now       = datetime.datetime.utcnow()
    try:
        for i in range(0, 100):
            user = users.User("ckchien@gmail.com")
            npo  = NpoProfile(npo_name=u"若水國際 - " + unicode(i), founder=u"張明正 & 王文華", google_acct=user, country=u"ROC", postal=u"104", state=u"Taiwan", city=u"Taipei",
                    district=u"大安區", founding_date=datetime.date(2007, 6, 1), authority=u"GOV", tag=[u"flow"],
                    status=u"new application", docs_link=[u"Timbuck2"], npo_rating=1, create_time=now, update_time=now)
            npo.put()
    except:
        response.write('大量新增 NpoProfile 失敗 (%s)' % str(sys.exc_info()))
        return response

    response.write('大量新增 NpoProfile 成功!!!')
    return response
