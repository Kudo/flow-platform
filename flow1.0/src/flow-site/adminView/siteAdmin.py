#-*- coding: cp950 -*-
import sys,cgi,re,time,os,datetime,math
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import TemplateDoesNotExist
from django.http import HttpResponseRedirect
from google.appengine.ext import db
from google.appengine.api import users
from db import ddl
from common import paging
import flowBase

displayCount = 20

def adminAccountList(request, errorMessage=None):
    if not isSiteAdmin():
        return HttpResponseRedirect(users.create_login_url(cgi.escape(request.path)))        

    objUser = users.get_current_user()
    if not objUser: 
        currentUser = "" 
    else: 
        currentUser = objUser.email()

    templateValue = {
        "base":         flowBase.getBase(request),
        "uriToAdd":     r'/admin/accounts/add',
        "uriToRemove":  r'/admin/accounts/remove',
        "currentUser":  users.get_current_user(),
        "adminList":    ddl.SiteAdmin.all(),
        "errorMessage": errorMessage
    }
    return render_to_response(r'admin/admin-managers.html', templateValue)

def addAdmin(request):
    if not isSiteAdmin():
        return HttpResponseRedirect(users.create_login_url(cgi.escape(request.path)))        

    errorMessage = None
    addEmail = db.UserProperty
    try:
        addEmail = users.User(request.POST['email'])
        if not ddl.SiteAdmin.all().filter('account =', addEmail).count():
            siteAdmin = ddl.SiteAdmin(account=addEmail)
            siteAdmin.put()
        else:
            errorMessage = ur'此帳號已經存在，不需再次加入。'
    except users.UserNotFoundError:
    	  errorMessage = ur'找不到此志工帳號 ' + request.POST['email'] + ur' 請檢查後再輸入。'

    #errorMessage = ddl.SiteAdmin.all().filter('account =', addEmail).count()
    return adminAccountList(request, errorMessage)

def removeAdmin(request):
    if not isSiteAdmin():
        return HttpResponseRedirect(users.create_login_url(cgi.escape(request.path)))        

    siteAdmin = ddl.SiteAdmin.all()
    siteAdmin.filter('account =', users.User(request.POST['email']))
    if siteAdmin:
    	  db.delete(siteAdmin)
    return adminAccountList(request, None)

def npoList(request):
    if not isSiteAdmin():
        return HttpResponseRedirect(users.create_login_url(cgi.escape(request.path)))        

    pageSet = paging.get(request.GET, ddl.NpoProfile.all().totalCount(), displayCount=displayCount)
    entryList = db.GqlQuery('SELECT * FROM NpoProfile ORDER BY id').fetch(displayCount, pageSet['entryOffset'])
        
    templateValue = {
        "base":                    flowBase.getBase(request, 'npo'),
        #"pageNav":                 PageNavigation(ddl.NpoProfile.all(), request, '/admin/npo'),
        "pageSet":                  pageSet,
        "entryList":                entryList,
    }
    return render_to_response(r'admin/admin-npo-list.html', templateValue)

def changeNpoStatus(request):
    if not isSiteAdmin():
        return HttpResponseRedirect(users.create_login_url(cgi.escape(request.path)))        

    if 'status' in request.REQUEST and 'npo_id' in request.REQUEST:
        status = request.REQUEST['status']
        npoID  = request.REQUEST['npo_id']
        npo    = db.get(npoID)
        if npo:
            npo.status = status
            npo.put()
    return npoList(request)

def volunteerList(request):
    if not isSiteAdmin():
        return HttpResponseRedirect(users.create_login_url(cgi.escape(request.path)))        

    pageSet = paging.get(request.GET, ddl.VolunteerProfile.all().totalCount(), displayCount=displayCount)
    entryList = db.GqlQuery('SELECT * FROM VolunteerProfile ORDER BY id').fetch(displayCount, pageSet['entryOffset'])
        
    templateValue = {
        "base":                    flowBase.getBase(request, 'admin'),
        #"pageNav":                 PageNavigation(ddl.VolunteerProfile.all(), request, '/admin/volunteer'),
        "pageSet":                  pageSet,
        "entryList":                entryList,
    }

    return render_to_response(r'admin/admin-volunteer-list.html', templateValue)

def changeVolunteerStatus(request):
    if not isSiteAdmin():
        return HttpResponseRedirect(users.create_login_url(cgi.escape(request.path)))        

    if 'status' in request.REQUEST and 'volunteer_id' in request.REQUEST:
        status = request.REQUEST['status']
        volunteerID = request.REQUEST['volunteer_id']
        volunteers = ddl.VolunteerProfile.all()
        volunteers.filter("volunteer_id =", users.User(volunteerID))
        if volunteers.count():
            volunteer = volunteers.get()
            volunteer.status = status
            volunteer.put()
    return volunteerList(request)

def eventList(request):
    if not isSiteAdmin():
        return HttpResponseRedirect(users.create_login_url(cgi.escape(request.path)))        

    pageSet = paging.get(request.GET, ddl.EventProfile.all().totalCount(), displayCount=displayCount)
    entryList = db.GqlQuery('SELECT * FROM EventProfile ORDER BY id').fetch(displayCount, pageSet['entryOffset'])
        
    templateValue = {
        "base":                    flowBase.getBase(request, 'admin'),
        #"pageNav":                 PageNavigation(ddl.EventProfile.all(), request, '/admin/event'),
        "pageSet":                  pageSet,
        "entryList":                entryList,
    }
    return render_to_response(r'admin/admin-event-list.html', templateValue)

def changeEventStatus(request):
    if not isSiteAdmin():
        return HttpResponseRedirect(users.create_login_url(cgi.escape(request.path)))        

    if 'status' in request.REQUEST and 'event_id' in request.REQUEST:
        status = request.REQUEST['status']
        eventID = request.REQUEST['event_id']
        events = ddl.EventProfile.all()
        events.filter("event_id =", eventID)
        if events.count():
            event = events.get()
            if status == r'_REMOVE_':
            	  event.delete()
            else:
                event.status = status
                event.put()
    return eventList(request)

def isSiteAdmin():
    if not users.is_current_user_admin():
        if not ddl.SiteAdmin.all().filter('account =', users.get_current_user()).count():
            return False
    return True

class PageNavigation:
    PageSize    = int()
    PageNo      = int()
    PageTotal   = int()
    RecordBegin = int()
    RecordEnd   = int()
    RecordTotal = int()
    RecordList  = []
    PageUri     = str()
    
    def __init__(self, objRecordList, objRequest, pageUri, pageSize=20):
        if 'page' in objRequest.REQUEST:
            self.PageNo = int(objRequest.REQUEST['page'])
        else:
            self.PageNo = 1

        self.PageSize = pageSize
        self.RecordTotal = objRecordList.count()
        self.PageTotal   = int(math.ceil(float(self.RecordTotal) / pageSize))
        self.RecordBegin = pageSize * (self.PageNo - 1) + 1
        if self.PageNo == self.PageTotal: 
            self.RecordEnd = self.RecordTotal
        else:
            self.RecordEnd = self.PageNo*pageSize

        self.RecordList = objRecordList.fetch(pageSize, self.RecordBegin - 1)


#def isAdminUser()
#    objUser=users.get_current_user()
#    if not objUser:
    	  # need to log in
#        return HttpResponseRedirect(users.create_login_url(cgi.escape(request.path)))

#    return True

