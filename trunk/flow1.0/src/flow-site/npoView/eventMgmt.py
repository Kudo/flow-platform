# -*- coding: big5 -*-
import datetime
from django.http import HttpResponseRedirect,HttpResponseForbidden
from django.shortcuts import render_to_response
from django import newforms as forms
from google.appengine.api import users
from google.appengine.ext import db
from db import ddl
import flowBase
from common import paging,emailUtil

dicRule = {'new application'        :{'modify':'',        'recruit':'disabled','validate':'disabled','close':'disabled','cancel':'','volunteer':'disabled'},
           'approved'               :{'modify':'disabled','recruit':''        ,'validate':'disabled','close':'disabled','cancel':'','volunteer':'disabled'},
           'announced'              :{'modify':'disabled','recruit':'disabled','validate':'disabled','close':'disabled','cancel':'','volunteer':'disabled'},
           'authenticating'         :{'modify':'',        'recruit':'disabled','validate':'disabled','close':'disabled','cancel':'','volunteer':'disabled'},
           'authenticated'          :{'modify':'disabled','recruit':''        ,'validate':'disabled','close':'disabled','cancel':'','volunteer':'disabled'},
           'registrating'           :{'modify':'disabled','recruit':''        ,'validate':''        ,'close':'disabled','cancel':'','volunteer':''},
           'recruiting'             :{'modify':'disabled','recruit':''        ,'validate':''        ,'close':'disabled','cancel':'','volunteer':''},
           'registration closed'    :{'modify':'disabled','recruit':'disabled','validate':''        ,'close':'disabled','cancel':'','volunteer':''},
           'on-going'               :{'modify':'disabled','recruit':''        ,'validate':'disabled','close':'disabled','cancel':'disabled','volunteer':''},
           'filling polls'          :{'modify':'disabled','recruit':'disabled','validate':'disabled','close':'disabled','cancel':'disabled','volunteer':'disabled'},
           'activity closed'        :{'modify':'disabled','recruit':'disabled','validate':'disabled','close':'disabled','cancel':'disabled','volunteer':'disabled'},
           'case-closed reporting'  :{'modify':'disabled','recruit':'disabled','validate':'disabled','close':''        ,'cancel':'disabled','volunteer':'disabled'},
           'cancelled'              :{'modify':'disabled','recruit':'disabled','validate':'disabled','close':'disabled','cancel':'disabled','volunteer':'disabled'},
           'abusive usage'          :{'modify':'disabled','recruit':'disabled','validate':'disabled','close':'disabled','cancel':'disabled','volunteer':'disabled'},
           'authenticating failed'  :{'modify':'disabled','recruit':'disabled','validate':'disabled','close':'disabled','cancel':'disabled','volunteer':'disabled'}
           }

dicStatusName={
    "new application":u'暫存',
    "approved":u'核准',
    "announced":u'發佈',
    "authenticating":u'未送審',
    "authenticated":u'送審中',
    "registrating":u'開放登記',
    "recruiting":u'招募中',
    "registration closed":u'結束登記',
    "on-going":u'活動進行中',
    "filling polls":u'填寫問卷',
    "activity closed":u'活動結束',
    "case-closed reporting":u'結案報告',
    "cancelled":u'已取消',
    "abusive usage":u'不當使用',
    "authenticating failed":u'認證失敗',
    }

def mainPage(request,npoid):
    objUser,objVolunteer,objNpo=flowBase.verifyNpo(request,npoid)
    if not objNpo:
        return HttpResponseForbidden(u'錯誤的操作流程')
    
    query = db.GqlQuery("SELECT * FROM EventProfile WHERE npo_profile_ref = :1 order by create_time desc",objNpo)
    # Todo: should handle more than 100 condition
    results = query.fetch(100)
    
    dic={'lstEvent' : actionCheck(results),
         'base': flowBase.getBase(request, 'npo'),
         'npoProfile': objNpo,
         'page': 'event'}
    return render_to_response(r'event/event-admin-list.html', dic)

def actionCheck(lstEvent):
    '''
    Match and added correct rule to each activity according its status.
    @return: active list with correct rule appended.
    '''
    lstActList = []
    
    for event in lstEvent:
        dic={"event_key":str(event.key()),
             "name":event.event_name,
             "status":dicStatusName[event.status],
             "dicPerm":dicRule[event.status]}
        lstActList.append(dic)
    return lstActList

class CancelEventForm(forms.Form):
    reason = forms.CharField(widget=forms.Textarea(attrs={'rows':'10', 'cols':'50','class':'field textarea medium'}))
    
def handleCancelEvent(request,npoid):
    objUser,objVolunteer,objNpo=flowBase.verifyNpo(request,npoid)
    if not objNpo:
        return HttpResponseForbidden(u'錯誤的操作流程')

    strEventKey=request.POST.get('event_key')
    if not strEventKey:
        return HttpResponseForbidden(u'錯誤的操作流程')
    event=db.get(db.Key(strEventKey))
    if event.npo_profile_ref.id!=objNpo.id:
        return HttpResponseForbidden(u'錯誤的操作流程')

    if 'submitType' in request.POST:
        form = CancelEventForm(data = request.POST)
        if form.is_valid():
            cancelDate=datetime.date.today()
            objRecSet = db.GqlQuery('select * from VolunteerEvent where event_profile_ref = :1', event)
            for objRec in objRecSet.fetch(1000):
                objRec.status="cancelled"
                objRec.cancelled=True
                objRec.cancel_date=cancelDate
                objRec.cancel_reason=form.clean_data['reason']
                emailUtil.sendEventCancelMail(objRec.volunteer_profile_ref,objRec.event_profile_ref,objRec.cancel_reason)
                objRec.put()
            event.status='cancelled'
            event.put()
            return HttpResponseRedirect('/npo/%s/admin/listEvent'%npoid)
    else:
        form = CancelEventForm()
    dic ={'event_key':strEventKey,
          'form': form,
          'base': flowBase.getBase(request, 'npo'),
          'npoProfile': objNpo,
          'page': 'event',
          'event': event}
    return render_to_response(r'event/event-admin-cancel.html', dic)
    
displayCount = 10
def volunteerList(request,npoid):
    objUser,objVolunteer,objNpo=flowBase.verifyNpo(request,npoid)
    if not objNpo:
        return HttpResponseForbidden(u'錯誤的操作流程')

    strEventKey=request.GET.get('event_key')
    if not strEventKey:
        return HttpResponseForbidden(u'錯誤的操作流程')
    event=db.get(db.Key(strEventKey))
    if event.npo_profile_ref.id!=objNpo.id:
        return HttpResponseForbidden(u'錯誤的操作流程')
    
    query = db.GqlQuery("SELECT * FROM VolunteerEvent WHERE event_profile_ref = :1 AND status = :2",event,'approved')
    # approvedVolunteers = query.fetch(1000)
    
    pageSet = paging.get(request.GET, query.count(), displayCount=displayCount)
    approvedVolunteers = query.fetch(displayCount, pageSet['entryOffset'])
    
    for volunteer in approvedVolunteers:
        volunteer.volunteer_profile_ref.showExpertise = u', '.join(volunteer.volunteer_profile_ref.expertise)
        
    
    dicData={'volunteers' : approvedVolunteers,
             'base':flowBase.getBase(request,'npo'),
             'event':event,
             'event_key':event.key(),
             'page':'event',
             'npoProfile':objNpo,
             'pageSet':                  pageSet,
             }
    return render_to_response(r'event/event-admin-volunteer-list.html', dicData)

def volunteerListLong(request,npoid):
    objUser,objVolunteer,objNpo=flowBase.verifyNpo(request,npoid)
    if not objNpo:
        return HttpResponseForbidden(u'錯誤的操作流程')

    strEventKey=request.GET.get('event_key')
    if not strEventKey:
        return HttpResponseForbidden(u'錯誤的操作流程')
    event=db.get(db.Key(strEventKey))
    if event.npo_profile_ref.id!=objNpo.id:
        return HttpResponseForbidden(u'錯誤的操作流程')
    
    query = db.GqlQuery("SELECT * FROM VolunteerEvent WHERE event_profile_ref = :1 AND status = :2",event,'approved')
    approvedVolunteers = query.fetch(1000)
    maillist = ''
    
    for volunteer in approvedVolunteers:
        maillist += volunteer.volunteer_profile_ref.gmail + ';'
        
    
    dicData={'volunteers' : approvedVolunteers,
             'base':flowBase.getBase(request,'npo'),
             'event':event,
             'event_key':event.key(),
             'page':'event',
             'npoProfile':objNpo,
             'maillist': maillist,
             }
    return render_to_response(r'event/event-admin-volunteer-list-long.html', dicData)
