#!/usr/bin/env python
# -*- coding: utf-8 -*-
import cgi
import md5
from google.appengine.api import users
from google.appengine.ext import db
from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from db import proflist
from db.ddl import *

COOKIE_ID = 'ACSID'             # Borrow this from GAE
def _make_token(request):
    if COOKIE_ID in request.COOKIES:
        return md5.new(settings.SECRET_KEY + request.COOKIES[COOKIE_ID]).hexdigest()
    return ''

def getBase(request):
    data = {}
    if not request:
        return data
    data['path']            = request.path
    data['full_path']       = request.get_full_path()
    data['user']            = users.get_current_user()
    data['volunteer']       = getVolunteer(data['user'])
    data['noLogo']          = '/static/images/head_blue50.jpg'
    data['proflist']        = getProfessionList()
    data['region']          = getRegion()
    data['token']           = _make_token(request)

    data['jQueryURI']       = settings.JQUERY_URI
    data['jQueryUI_URI']    = settings.JQUERY_UI_URI

    return data

def getVolunteer(volunteer_id=users.get_current_user()):
    if not volunteer_id:
        return None
    if isinstance(volunteer_id, (str, unicode)):
        volunteer_id = users.User(volunteer_id)
    return db.GqlQuery('SELECT * FROM VolunteerProfile WHERE volunteer_id = :1', volunteer_id).get()

def getNpo(id=None):
    if not id:
        return None
    return db.GqlQuery('SELECT * FROM NpoProfile WHERE id = :1', id).get()

def getVolunteerBase(volunteer, displayFriendCount=6, displayNpoCount=6):
    data = {}
    if not volunteer:
        return data

    data['volunteer_id']    = volunteer.volunteer_id
    data['name']            = u', '.join([volunteer.volunteer_first_name, volunteer.volunteer_last_name])
    data['birthday']        = volunteer.date_birth.strftime('%Y 年 %m 月 %d 日')
    data['resident']        = volunteer.resident_city
    data['logo']            = volunteer.logo
    #data['friendCount']     = len(volunteer.friends)
    data['npoCount']        = len(volunteer.npo_profile_ref)

    # friends
    #tmp = [VolunteerProfile.get(volunteer.friends[i]) for i in range(displayFriendCount) if i < len(volunteer.friends)]
    #data['friends']         = [tmp[i:i+3] for i in range(0, displayFriendCount, 3) if i < len(tmp)]

    # npo
    tmp = [NpoProfile.get(volunteer.npo_profile_ref[i]) for i in range(displayNpoCount) if i < len(volunteer.npo_profile_ref)]
    data['npos']             = [tmp[i:i+3] for i in range(0, displayNpoCount, 3) if i < len(tmp)]

    del tmp
    return data

def getNpoBase(npo):
    data = {}
    if not npo:
        return data
    data['npo_name']        = npo.npo_name

    return data

def login(request):
    if 'redirect' in request.GET:
        return HttpResponseRedirect(users.create_login_url('/loginProxy?redirect=' + cgi.escape(request.GET['redirect'])))
    else:
        return HttpResponseRedirect(users.create_login_url('/loginProxy'))

def loginProxy(request):
    base = getBase(request)
    if 'redirect' in request.GET:
        redirectURI = request.GET['redirect']
    else:
        redirectURI = '/'

    if getVolunteer(base['user']):
        loginSuccess = True
    else:
        loginSuccess = False

    template_values = {
        'base':                 base,
        'redirectURI':          redirectURI,
        'loginSuccess':         loginSuccess,
    }
    return render_to_response('loginProxy.html', template_values)

def logout(request):
    if 'redirect' in request.GET:
        return HttpResponseRedirect(users.create_logout_url(cgi.escape(request.GET['redirect'])))
    else:
        return HttpResponseRedirect(users.create_logout_url('/'))

def getProfessionList():
	return proflist.getProfessionList()

def getRegion(getProperty=False):
    regions = db.GqlQuery('SELECT * FROM CountryCity WHERE state_en = :1', 'Taiwan').fetch(50)
    if getProperty:
        return regions
    return [region.city_tc for region in regions]
