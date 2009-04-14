# -*- coding: big5 -*-
import datetime
from django.http import HttpResponseRedirect,HttpResponseForbidden
from django.shortcuts import render_to_response
from django.template import TemplateDoesNotExist
from google.appengine.ext import db
from db import ddl
from django import newforms as forms
import flowBase

# Check to see if eventID is given. Direct to error page if not.
def volunteerShow(request):
    objUser,objVolunteer,objNpo=flowBase.verifyNpo(request)
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
        objVolunteer = volEvent.volunteer_profile_ref
        objVolunteer.age = (datetime.date.today() - objVolunteer.date_birth).days / 365
        objVolunteer.dbKey = volEvent.key()
        objVolunteer.expertiseSum=fixedSizeStr(u','.join(objVolunteer.expertise),6)
        lstVolunteer.append(objVolunteer)
    return lstVolunteer

def approveVolunteer(request):
    objUser,objVolunteer,objNpo=flowBase.verifyNpo(request)
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
    
    # Process the data in form.cleaned_data
    query = db.GqlQuery("SELECT * FROM VolunteerEvent WHERE event_profile_ref = :1 AND status = :2",event,'approved')
    lstPreApproved = query.fetch(1000)
    if 'approved' not in request.POST:
        return HttpResponseRedirect('/npo/admin/listEvent')
    lstApprovedVol = request.POST['approved']
    if not isinstance(lstApprovedVol,list) or not isinstance(lstApprovedVol,tuple):
        lstApprovedVol=[lstApprovedVol]
    for volKey in lstApprovedVol:
        vol=db.get(db.Key(volKey))
        if vol in lstPreApproved:
            lstPreApproved.remove(vol)
            continue
        vol.status='approved'
        vol.approved_time=datetime.datetime.utcnow()
        vol.put()
    event.approved_count=len(lstApprovedVol)
    event.volunteer_shortage=event.volunteer_req-event.approved_count
    event.put()
    for vol in lstPreApproved:
        raise RuntimeError(vol)
    return volunteerShow(request)
    

