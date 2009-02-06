#!/usr/bin/env python
# -*- coding: utf-8 -*-
import cgi
from google.appengine.api import users
from google.appengine.ext import db
from django.http import HttpResponseRedirect
from db.ddl import *

def getBase(request, volunteer=None):
    data = {}
    if not request:
        return data
    data['path']            = request.path
    data['full_path']       = request.get_full_path()
    data['user']            = users.get_current_user()

    if volunteer:
        if isinstance(volunteer, (str, unicode)):
            volunteer = getVolunteer(volunteer)
        data.update(getVolunteerBase(volunteer))

    return data

def getVolunteer(volunteer_id=users.get_current_user()):
    if not volunteer_id:
        return None
    return db.GqlQuery('SELECT * FROM VolunteerProfile WHERE volunteer_id = :1',volunteer_id).get()

def getVolunteerBase(volunteer, displayFriendCount=6, displayNpoCount=6):
    data = {}
    if not volunteer:
        return data

    data['volunteer_id']    = volunteer.volunteer_id
    data['name']            = '%s, %s' % (volunteer.volunteer_first_name, volunteer.volunteer_last_name)
    data['birthday']        = volunteer.date_birth.strftime('%Y 年 %m 月 %d 日')
    data['resident']        = volunteer.resident_city
    data['logo']            = volunteer.logo
    data['noLogo']          = '/static/images/head_blue50.jpg'
    data['friendCount']     = len(volunteer.friends)
    data['npoCount']        = len(volunteer.npo_profile_ref)
    data['token']           = ''

    # friends
    tmp = [VolunteerProfile.get(volunteer.friends[i]) for i in range(displayFriendCount) if i < len(volunteer.friends)]
    data['friends']         = [tmp[i:i+3] for i in range(0, displayFriendCount, 3) if i < len(tmp)]

    # npo
    tmp = [VolunteerProfile.get(volunteer.npo_profile_ref[i]) for i in range(displayNpoCount) if i < len(volunteer.npo_profile_ref)]
    data['npos']             = [tmp[i:i+3] for i in range(0, displayNpoCount, 3) if i < len(tmp)]

    del tmp
    return data

def login(request):
    if 'redirect' in request.GET:
        return HttpResponseRedirect(users.create_login_url(cgi.escape(request.GET['redirect'])))
    else:
        return HttpResponseRedirect(users.create_login_url('/'))

def logout(request):
    if 'redirect' in request.GET:
        return HttpResponseRedirect(users.create_logout_url(cgi.escape(request.GET['redirect'])))
    else:
        return HttpResponseRedirect(users.create_logout_url('/'))
