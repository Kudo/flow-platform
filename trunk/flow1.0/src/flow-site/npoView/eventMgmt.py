import datetime
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import TemplateDoesNotExist
from google.appengine.api import users
from django import newforms as forms
from google.appengine.ext import db
from db import ddl
import flowBase

dicRule = {'new application'        :{'modify':'','recruit':'disabled','validate':'disabled','close':'disabled','cancel':''},
           'approved'               :{'modify':'disabled','recruit':'','validate':'disabled','close':'disabled','cancel':''},
           'announced'              :{'modify':'disabled','recruit':'disabled','validate':'disabled','close':'disabled','cancel':''},
           'authenticating'         :{'modify':'','recruit':'disabled','validate':'disabled','close':'disabled','cancel':''},
           'authenticated'          :{'modify':'disabled','recruit':'','validate':'disabled','close':'disabled','cancel':''},
           'registrating'           :{'modify':'disabled','recruit':'','validate':'','close':'disabled','cancel':''},
           'recruiting'             :{'modify':'disabled','recruit':'','validate':'','close':'disabled','cancel':''},
           'registration closed'    :{'modify':'disabled','recruit':'disabled','validate':'','close':'disabled','cancel':'disabled'},
           'on-going'               :{'modify':'disabled','recruit':'','validate':'','close':'disabled','cancel':'disabled'},
           'filling polls'          :{'modify':'disabled','recruit':'disabled','validate':'disabled','close':'disabled','cancel':'disabled'},
           'activity closed'        :{'modify':'disabled','recruit':'disabled','validate':'disabled','close':'disabled','cancel':'disabled'},
           'case-closed reporting'  :{'modify':'disabled','recruit':'disabled','validate':'disabled','close':'','cancel':'disabled'},
           'cancelled'              :{'modify':'disabled','recruit':'disabled','validate':'disabled','close':'disabled','cancel':'disabled'},
           'abusive usage'          :{'modify':'disabled','recruit':'disabled','validate':'disabled','close':'disabled','cancel':'disabled'}
           }

def mainPage(request):
    objUser=users.get_current_user()
    if not objUser:
        return HttpResponseRedirect('/')
    objVolunteer=flowBase.getVolunteer(objUser)
    if not objVolunteer:
        return HttpResponseRedirect('/')
    objNpo=flowBase.getNpoByUser(objUser)
    if not objNpo:
        return HttpResponseRedirect('/')
    
    query = db.GqlQuery("SELECT * FROM EventProfile WHERE npo_profile_ref = :1",objNpo)
    results = query.fetch(100)
    return render_to_response(r'event/event-admin-list.html', {'lstActivityList' : actionCheck(results), 'base': flowBase.getBase(request)})

def actionCheck(lstEvent):
    '''
    Match and added correct rule to each activity according its status.
    @return: active list with correct rule appended.
    '''
    lstActList = []
    
    for event in lstEvent:
        lstActList.append({"event_key":str(event.key()),"name":event.event_name,"status":event.status,"dicPerm":dicRule[event.status]})
    return lstActList

class CancelEventForm(forms.Form):
    reason = forms.CharField(widget=forms.Textarea(attrs={'rows':'10', 'cols':'50','class':'field textarea medium'}))
    

def showCancelEvent(request):
    strEventKey=request.POST.get('event_key')
    event=db.get(db.Key(strEventKey))
    dic ={'event_key':strEventKey,
          'form': CancelEventForm(),
          'base': flowBase.getBase(request),
          'event': event}
    return render_to_response(r'event/event-admin-cancel.html', dic)

def handleCancelEvent(request):
    strEventKey=request.POST.get('event_key')
    if not strEventKey:
        return HttpResponseRedirect('/npo/listEvent')
    event=db.get(db.Key(strEventKey))
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
        return HttpResponseRedirect('/npo/listEvent')
    else:
        dic ={'event_key':strEventKey,
              'form': form,
              'base': flowBase.getBase(request),
              'event': event}
        return render_to_response(r'event/event-admin-cancel.html', dic)
    