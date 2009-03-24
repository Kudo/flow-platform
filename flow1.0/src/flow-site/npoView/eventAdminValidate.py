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
        return HttpResponseForbidden(u'錯誤的操作流程')

    if request.method != 'POST' or 'event_key' not in request.POST:
        return HttpResponseForbidden(u'錯誤的操作流程')

    eventKey = request.POST['event_key']
    event=db.get(db.Key(eventKey))
    if None == event:
        return HttpResponseForbidden(u'資料不存在! key:%s'%eventKey)
    if event.npo_profile_ref.id!=objNpo.id:
        return HttpResponseForbidden(u'錯誤的操作流程')

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

# append volunteer name from volunteer profile
def addName(lstVolEvent):
    lstVolunteer=[]
    for volEvent in lstVolEvent:
        objVolunteer = volEvent.volunteer_profile_ref
        objVolunteer.age = (datetime.date.today() - objVolunteer.date_birth).days / 365
        objVolunteer.dbKey = volEvent.key()
        lstVolunteer.append(objVolunteer)
    return lstVolunteer

def approveVolunteer(request):
    objUser,objVolunteer,objNpo=flowBase.verifyNpo(request)
    if not objNpo:
        return HttpResponseForbidden(u'錯誤的操作流程')

    if request.method != 'POST' or 'event_key' not in request.POST:
        return HttpResponseForbidden(u'錯誤的操作流程')

    eventKey = request.POST['event_key']
    event=db.get(db.Key(eventKey))
    if None == event:
        return HttpResponseForbidden(u'資料不存在! key:%s'%eventKey)
    if event.npo_profile_ref.id!=objNpo.id:
        return HttpResponseForbidden(u'錯誤的操作流程')
    
    # Process the data in form.cleaned_data
    query = db.GqlQuery("SELECT * FROM VolunteerEvent WHERE event_profile_ref = :1 AND status = :2",event,'approved')
    lstPreApproved = query.fetch(1000)
    if 'approved' not in request.POST:
        return HttpResponseRedirect('listEvent')
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
    

