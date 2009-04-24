# -*- coding: big5 -*-
import datetime,logging
from django.http import HttpResponseRedirect,HttpResponseForbidden
from django.shortcuts import render_to_response
from django.template import TemplateDoesNotExist
from google.appengine.ext import db
from db import ddl
from django import newforms as forms
import flowBase
from common import emailUtil

# Check to see if eventID is given. Direct to error page if not.
def volunteerShow(request,npoid):
    objUser,objVolunteer,objNpo=flowBase.verifyNpo(request,npoid)
    if not objNpo:
        raise AssertionError("objNpo is None")

    if request.method != 'POST' or 'event_key' not in request.POST:
        raise AssertionError("request.method != 'POST' or 'event_key' not in request.POST")

    eventKey = request.POST['event_key']
    event=db.get(db.Key(eventKey))
    if None == event:
        raise AssertionError("event is None")
    if event.npo_profile_ref.id!=objNpo.id:
        raise AssertionError("event.npo_profile_ref.id!=objNpo.id")

    # Retrieve data with given eventID and status
    query = db.GqlQuery("SELECT * FROM VolunteerEvent WHERE event_profile_ref = :1 AND status = :2",event,'new registration')
    result1 = query.fetch(1000)
    query = db.GqlQuery("SELECT * FROM VolunteerEvent WHERE event_profile_ref = :1 AND status = :2",event,'approved')
    result2 = query.fetch(1000)
    dicData={'lstVolunteer' : addName(result1),
             'lstApproved' : addName(result2),
             'base':flowBase.getBase(request,'npo'),
             'npoProfile': objNpo,
             'event':event,
             'event_key':event.key(),
             'page':'event'
             }
    return render_to_response(r'event/event-admin-validate.html', dicData)

def fixedSizeStr(s,intSize):
    if type(s)!=type(u''):
        s=unicode(s,'utf-8')
    return s[:intSize]+u'...'

# append volunteer name from volunteer profile
def addName(lstVolEvent):
    lstVolunteer=[]
    for volEvent in lstVolEvent:
        try:
            objVolunteer = volEvent.volunteer_profile_ref
        except:
            continue
        objVolunteer.age = (datetime.date.today() - objVolunteer.date_birth).days / 365
        objVolunteer.dbKey = volEvent.key()
        objVolunteer.expertiseSum=fixedSizeStr(u','.join(objVolunteer.expertise),6)
        lstVolunteer.append(objVolunteer)
    return lstVolunteer

def approveVolunteer(request,npoid):
    objUser,objVolunteer,objNpo=flowBase.verifyNpo(request,npoid)
    if not objNpo:
        raise AssertionError("objNpo is None")

    if request.method != 'POST' or 'event_key' not in request.POST:
        raise AssertionError("request.method != 'POST' or 'event_key' not in request.POST")

    eventKey = request.POST['event_key']
    event=db.get(db.Key(eventKey))
    if None == event:
        raise AssertionError("event is None")
    if event.npo_profile_ref.id!=objNpo.id:
        raise AssertionError("event.npo_profile_ref.id!=objNpo.id")
    if 'approved' not in request.POST or event.volunteer_shortage==0:
        return HttpResponseRedirect('/npo/%s/admin/listEvent'%npoid)
    
    # Process the data in form.cleaned_data
    query = db.GqlQuery("SELECT * FROM VolunteerEvent WHERE event_profile_ref = :1 AND status = :2",event,'approved')
    lstPreApproved = [obj.volunteer_profile_ref for obj in query.fetch(1000)]
    event.approved_count=len(lstPreApproved)
    event.volunteer_shortage=event.volunteer_req-event.approved_count
    lstApprovedVol = request.POST['approved']
    if not isinstance(lstApprovedVol,list) and not isinstance(lstApprovedVol,tuple):
        lstApprovedVol=[lstApprovedVol]
    for volKey in lstApprovedVol:
        objRec=db.get(db.Key(volKey))
        if not objRec:
            continue
        if objRec in lstPreApproved:
            lstPreApproved.remove(objRec)
            continue
        objRec.status='approved'
        objRec.approved_time=datetime.datetime.utcnow()
        emailUtil.sendJoinEventApprovedMail(objRec.volunteer_profile_ref,event)
        objRec.put()
        event.approved_count+=1
    event.volunteer_shortage=event.volunteer_req-event.approved_count
    event.put()
    return volunteerShow(request,npoid)
    

