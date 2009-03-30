#!/usr/bin/env python
# -*- coding: utf-8 -*-
import cgi,logging
import md5
from google.appengine.api import users,memcache
from google.appengine.ext import db
from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from db import proflist, regionList
from db.ddl import *

def makeToken(request, volunteer_id):
    COOKIE_ID_LIST = ['ACSID', 'dev_appserver_login']
    if volunteer_id:
        cacheName = 'LoginCache/token/%s' % volunteer_id
        cacheObj = memcache.get(cacheName)
        if cacheObj:
            return cacheObj
        for COOKIE_ID in COOKIE_ID_LIST:
            if COOKIE_ID in request.COOKIES:
                token = md5.new(settings.SECRET_KEY + request.COOKIES[COOKIE_ID]).hexdigest()
                memcache.add(cacheName, token, 7200)
                return token
    return ''

def getBase(request, category = 'homepage'):
    data = {}
    if not request:
        return data
    data['path']            = request.path
    data['full_path']       = request.get_full_path()
    data['user']            = users.get_current_user()
    data['volunteer_id']    = getVolunteerID(data['user'])
    data['noLogo']          = '/static/images/head_blue50.jpg'
    data['proflist']        = getProfessionList()
    data['resident']        = getResident()
    data['region']          = getRegion()
    data['token']           = makeToken(request, data['volunteer_id'])

    data['jQueryURI']       = settings.JQUERY_URI
    data['jQueryUI_URI']    = settings.JQUERY_UI_URI
    
    data['isFlowAdmin']     = True if isFlowAdmin() else False
    
    # Added by Tom, workaround
    data['cat_' + category]          = True

    return data

def getVolunteer(volunteer_id=users.get_current_user()):
    if not volunteer_id:
        return None
    if isinstance(volunteer_id, (str, unicode)):
        volunteer_id = users.User(volunteer_id)
    return VolunteerProfile.get_by_key_name(str(volunteer_id))

def getVolunteerID(volunteer_id=users.get_current_user()):
    if not volunteer_id:
        return None
    if isinstance(volunteer_id, (str, unicode)):
        volunteer_id = users.User(volunteer_id)
    if memcache.get('LoginCache/volunteer_id/%s' % volunteer_id):
        return volunteer_id
    elif VolunteerProfile.get_by_key_name(str(volunteer_id)):
        memcache.add('LoginCache/volunteer_id/%s' % volunteer_id, '1', 3600)
        return volunteer_id
    else:
        return None

def getNpo(id=None):
    if not id:
        return None
    return db.GqlQuery('SELECT * FROM NpoProfile WHERE id = :1', id).get()

def getNpoByUser(user):
    npo = db.GqlQuery('SELECT * FROM NpoProfile WHERE google_acct = :1', user).get()
    return npo

def getVolunteerBase(volunteer, displayFriendCount=6, displayNpoCount=6):
    data = {}
    if not volunteer:
        return data

    data['volunteer_id']    = volunteer.volunteer_id
    data['name']            = u', '.join([volunteer.volunteer_first_name, volunteer.volunteer_last_name])
    data['birthday']        = volunteer.date_birth.strftime('%Y 年 %m 月 %d 日')
    data['resident']        = volunteer.resident_city
    data['logo']            = volunteer.logo
    data['feedUri']         = volunteer.saved_feed_link or ''
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
        if request.GET['redirect'] == '/volunteer/register/step3/':
            return HttpResponseRedirect(users.create_login_url('/volunteer/register/step3'))
        else:
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
    objUser = users.get_current_user()
    if objUser:
        memcache.delete('LoginCache/volunteer_id/%s' % objUser)
    if 'redirect' in request.GET:
        return HttpResponseRedirect(users.create_logout_url(cgi.escape(request.GET['redirect'])))
    else:
        return HttpResponseRedirect(users.create_logout_url('/'))

def getProfessionList():
	return proflist.getProfessionList()

def getResident():
    regions = memcache.get('Region/Residient')
    if not regions:
        regions = regionList.getResidentList()
        memcache.add('Region/Resident', regions, 604800)
    return regions

def getRegion():
    regions = memcache.get('Region/Region')
    if not regions:
        regions = regionList.getRegionList()
        memcache.add('Region/Region', regions, 604800)
    return regions + getResident()

def verifyVolunteer(request):
    if 'volunteer_id' not in request.GET:
        if users.get_current_user():
            userObj = users.get_current_user()
        else:
            return None
    else:
        userObj = users.User(cgi.escape(request.GET['volunteer_id']))
    return getVolunteer(userObj)

def verifyNpo(request):
    objUser=users.get_current_user()
    if not objUser:
        logging.critical('invalid request from %s for %s',request.META.get('REMOTE_ADDR'),request.path)
        return (None,None,None)
    objVolunteer=getVolunteer(objUser)
    if not objVolunteer:
        logging.critical('invalid request from %s[%s] for %s',objUser,request.META.get('REMOTE_ADDR'),request.path)
        return (objUser,None,None)
    objNpo=getNpoByUser(objUser)
    if not objNpo:
        logging.critical('invalid request from %s[%s] for %s',objUser,request.META.get('REMOTE_ADDR'),request.path)
        return (objUser,objVolunteer,None)
    return (objUser,objVolunteer,objNpo)

def isFlowAdmin():
    if users.is_current_user_admin() or SiteAdmin.all().filter('account =', users.get_current_user()).get():
        return True
    return False
