# -*- coding: big5 -*-
import datetime
from django.http import HttpResponseRedirect,HttpResponseForbidden
from django.shortcuts import render_to_response
from django.template import TemplateDoesNotExist
from google.appengine.api import users
from django import newforms as forms
from google.appengine.ext import db
from db import ddl
import flowBase

dicRule = {'new application'        :{'modify':'',        'recruit':'disabled','validate':'disabled','close':'disabled','cancel':''},
           'approved'               :{'modify':'disabled','recruit':''        ,'validate':'disabled','close':'disabled','cancel':''},
           'announced'              :{'modify':'disabled','recruit':'disabled','validate':'disabled','close':'disabled','cancel':''},
           'authenticating'         :{'modify':'',        'recruit':'disabled','validate':'disabled','close':'disabled','cancel':''},
           'authenticated'          :{'modify':'disabled','recruit':''        ,'validate':'disabled','close':'disabled','cancel':''},
           'registrating'           :{'modify':'disabled','recruit':''        ,'validate':''        ,'close':'disabled','cancel':''},
           'recruiting'             :{'modify':'disabled','recruit':''        ,'validate':''        ,'close':'disabled','cancel':''},
           'registration closed'    :{'modify':'disabled','recruit':'disabled','validate':''        ,'close':'disabled','cancel':''},
           'on-going'               :{'modify':'disabled','recruit':''        ,'validate':'disabled','close':'disabled','cancel':'disabled'},
           'filling polls'          :{'modify':'disabled','recruit':'disabled','validate':'disabled','close':'disabled','cancel':'disabled'},
           'activity closed'        :{'modify':'disabled','recruit':'disabled','validate':'disabled','close':'disabled','cancel':'disabled'},
           'case-closed reporting'  :{'modify':'disabled','recruit':'disabled','validate':'disabled','close':''        ,'cancel':'disabled'},
           'cancelled'              :{'modify':'disabled','recruit':'disabled','validate':'disabled','close':'disabled','cancel':'disabled'},
           'abusive usage'          :{'modify':'disabled','recruit':'disabled','validate':'disabled','close':'disabled','cancel':'disabled'}
           }

dicStatusName={
    "new application":u'�Ȧs',
    "approved":u'�֭�',
    "announced":u'�o�G',
    "authenticating":u'���e�f',
    "authenticated":u'�e�f��',
    "registrating":u'�}��n�O',
    "recruiting":u'�۶Ҥ�',
    "registration closed":u'�����n�O',
    "on-going":u'���ʶi�椤',
    "filling polls":u'��g�ݨ�',
    "activity closed":u'���ʵ���',
    "case-closed reporting":u'���׳��i',
    "cancelled":u'�w����',
    "abusive usage":u'����ϥ�',
    }

def mainPage(request):
    objUser,objVolunteer,objNpo=flowBase.verifyNpo(request)
    if not objNpo:
        return HttpResponseForbidden(u'���~���ާ@�y�{')
    
    query = db.GqlQuery("SELECT * FROM EventProfile WHERE npo_profile_ref = :1",objNpo)
    # Todo: should handle more than 100 condition
    results = query.fetch(100)
    dic={'lstEvent' : actionCheck(results),
         'base': flowBase.getBase(request, 'npo'),
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
    
def handleCancelEvent(request):
    objUser,objVolunteer,objNpo=flowBase.verifyNpo(request)
    if not objNpo:
        return HttpResponseForbidden(u'���~���ާ@�y�{')

    strEventKey=request.POST.get('event_key')
    if not strEventKey:
        return HttpResponseForbidden(u'���~���ާ@�y�{')
    event=db.get(db.Key(strEventKey))
    if event.npo_profile_ref.id!=objNpo.id:
        return HttpResponseForbidden(u'���~���ާ@�y�{')

    if 'submitType' in request.POST:
        form = CancelEventForm(data = request.POST)
        if form.is_valid():
            event.status='cancelled'
            event.put()
            cancelDate=datetime.date.today()
            objRecSet = db.GqlQuery('select * from VolunteerEvent where event_profile_ref = :1', event)
            for objRec in objRecSet.fetch(100):
                objRec.status="cancelled"
                objRec.cancelled=True
                objRec.cancel_date=cancelDate
                objRec.cancel_reason=form['reason'].data
                objRec.put()
                # Todo: send email to regitered use
            return HttpResponseRedirect('listEvent')
    else:
        form = CancelEventForm()
    dic ={'event_key':strEventKey,
          'form': form,
          'base': flowBase.getBase(request, 'npo'),
          'page': 'event',
          'event': event}
    return render_to_response(r'event/event-admin-cancel.html', dic)
    