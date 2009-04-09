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
    data['myNpoList']       = getNpoListByVolunteer(getVolunteer(data['user']))
    data['isFlowAdmin']     = True if isFlowAdmin() else False
    
    data['noLogo']          = '/static/images/volunteer50.gif'
    data['noLogo75']        = '/static/images/volunteer75.gif'
    data['noLogo100']       = '/static/images/volunteer100.gif'
    data['noNpoLogo']       = '/static/images/NPO50.gif'
    data['noNpoLogo75']     = '/static/images/NPO75.gif'
    data['noNpoLogo100']    = '/static/images/NPO100.gif'
    data['proflist']        = getProfessionList()
    data['resident']        = getResident()
    data['region']          = getRegion()
    data['token']           = makeToken(request, data['volunteer_id'])

    data['jQueryURI']       = settings.JQUERY_URI
    data['jQueryUI_URI']    = settings.JQUERY_UI_URI

    # Added by Tom, workaround
    data['cat_' + category]          = True

    return data

def getVolunteer(volunteer_id):
    if not volunteer_id:
        return None
    if isinstance(volunteer_id, (str, unicode)):
        volunteer_id = users.User(volunteer_id)
    return VolunteerProfile.get_by_key_name(str(volunteer_id))

def getVolunteerByKey(key):
    if not key:
        return None
    return VolunteerProfile.get(key)

def getVolunteerID(volunteer_id):
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

def getNpo(id=None, npo_id=None):
    if id:
        return NpoProfile.all().filter('id =', id).get()
    if npo_id:
        return NpoProfile.all().filter('npo_id =', npo_id).get()
    return None

def getNpoByUser(user):
    npo = db.GqlQuery('SELECT * FROM NpoProfile WHERE google_acct = :1', user).get()
    return npo

def getNpoListByVolunteer(volunteer):
    """
    Get NPO List for one user
    return [{'npo_id': npo_id, 'npo_name': npo_name, 'isAdmin': True/False, 'key': __key__}]
    """
    if not volunteer:
        return []
    npoList = {}
    for key in volunteer.npo_profile_ref:
        npoObj = NpoProfile.get(key)
        key = str(key)
        npoList[key] = {'npo_id': npoObj.npo_id, 'npo_name': npoObj.npo_name, 'isAdmin': False, 'key': key}
    for adminObj in volunteer.admins2volunteer.fetch(1000):
        npoObj = adminObj.npo_profile_ref
        npoKey = str(npoObj.key())
        npoList[npoKey] = {'npo_id': npoObj.npo_id, 'npo_name': npoObj.npo_name, 'isAdmin': True, 'key': npoKey}
    return list(npoList.values())

def getVolunteerBase(volunteer, displayFriendCount=6, displayNpoCount=6):
    data = {}
    if not volunteer:
        return data

    data['key']             = volunteer.key()
    data['volunteer_id']    = volunteer.volunteer_id
    data['realname']        = u', '.join([volunteer.volunteer_last_name, volunteer.volunteer_first_name])
    data['nickname']        = volunteer.nickname
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
    data['npo_id']          = npo.npo_id
    data['isNpoAdmin']      = isNpoAdmin(npo = npo)

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
        memcache.delete('LoginCache/token/%s' % objUser)
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

def verifyVolunteer(request, key=None):
    if not key:
        return getVolunteer(users.get_current_user())
    else:
        return getVolunteerByKey(key)

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

def isNpoAdmin(volunteer=None, npo=None):
    """
    Given a volunteer, to check if he or she is a NPO admin.
    if given npo as parameter, this function will check for specific NPO.
    otherwise, it will check if the volunteer has a NPO admin role for any NPO.
    """
    
    if not volunteer:
        volunteer = getVolunteer(users.get_current_user())
        if not volunteer:
            return False

    if npo.key() and npo.admins2npo.filter('volunteer_profile_ref = ', volunteer).count():
        return True
    elif not npo and volunteer.admins2volunteer.get():
        return True
    return False

def addVolunteer2Npo(volunteer, npo):
    if volunteer and npo and volunteer.key() not in npo.members:
        volunteer.npo_profile_ref.append(npo.key())
        volunteer.put()
        npo.members.append(volunteer.key())
        npo.put()
        return True
    return False

def addVolunteer2NpoAdmin(volunteer, npo):
    if volunteer and npo and not NpoAdmin.all().filter('npo_profile_ref = ', npo).filter('volunteer_profile_ref = ', volunteer).get():
        npoAdminObj = NpoAdmin(npo_profile_ref=npo, admin_role='Main', volunteer_profile_ref=volunteer)
        npoAdminObj.put()
        return True
    return False
