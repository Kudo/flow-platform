# -*- coding: big5 -*-
import time, re, datetime,logging
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render_to_response
from google.appengine.ext import db
from google.appengine.api import users
from django import newforms as forms
from db import ddl
from google.appengine.ext.db import djangoforms
from common.widgets import FlowSplitDateTimeWidget
import flowBase

class NewEventForm(djangoforms.ModelForm):
    event_name = forms.CharField(widget=forms.TextInput(attrs={'size':'37'}))
    description = forms.CharField(widget=forms.Textarea(attrs={'rows':'4', 'cols':'40'}))
    start_time = forms.SplitDateTimeField(widget=FlowSplitDateTimeWidget())
    end_time = forms.SplitDateTimeField(widget=FlowSplitDateTimeWidget())
    reg_start_time = forms.SplitDateTimeField(widget=FlowSplitDateTimeWidget())
    reg_end_time = forms.SplitDateTimeField(widget=FlowSplitDateTimeWidget())
    event_region = forms.CharField(widget=forms.TextInput(attrs={'size':'59'}))
    event_hours = forms.IntegerField(min_value=0,initial=1,widget=forms.TextInput(attrs={'size':'20'}))
    event_target = forms.CharField(widget=forms.TextInput(attrs={'size':'38'}))    
    objective = forms.CharField(widget=forms.TextInput(attrs={'size':'49'}))
    summary = forms.CharField(required=False,widget=forms.Textarea(attrs={'rows':'4', 'cols':'40'}))
    expense = forms.IntegerField(required=False,widget=forms.TextInput(attrs={'size':'20'}))
    registration_fee = forms.IntegerField(required=False,widget=forms.TextInput(attrs={'size':'20'}))
    attachment_links_show = forms.URLField(required=False,initial='',widget=forms.TextInput(attrs={'size':'58'}))
    min_age = forms.IntegerField(min_value=1,initial=1,widget=forms.TextInput(attrs={'size':'3'}))
    max_age = forms.IntegerField(min_value=1,initial=99,widget=forms.TextInput(attrs={'size':'3'}))
    volunteer_req = forms.IntegerField(required=True,min_value=1,initial=1,widget=forms.TextInput(attrs={'size':'3'}))
   
    class Meta:
        event_fields = ['event_name', 'description', 'start_time','end_time','reg_start_time','reg_end_time',
                        'event_region', 'event_hours', 'event_target', 'tag', 'objective', 'summary', 'expense',
                        'registration_fee','attachment_links_show','event_zip','event_field','category']
        volunteer_fileds = ['sex','max_age', 'min_age','volunteer_req','expertise_req','join_flow_plan']
        model = ddl.EventProfile
        fields = event_fields + volunteer_fileds

    def clean_end_time(self):
        if self.clean_data['end_time']<=self.clean_data['start_time']:
            raise forms.ValidationError(u'�}�l�ɶ��j�󵲧��ɶ�')
        return self.clean_data['end_time']
    def clean_reg_end_time(self):
        if self.clean_data['reg_end_time']<=self.clean_data['reg_start_time']:
            raise forms.ValidationError(u'�}�l�ɶ��j�󵲧��ɶ�')
        return self.clean_data['reg_end_time']
    def clean_max_age(self):
        if 'minx_age' in self.clean_data:
            if self.clean_data['max_age']<self.clean_data['min_age']:
                raise forms.ValidationError(u'�̤p�~�ֶW�L�̤j�~��')
        return self.clean_data['max_age']
    def clean_min_age(self):
        if 'max_age' in self.clean_data:
            if self.clean_data['max_age']<self.clean_data['min_age']:
                raise forms.ValidationError(u'�̤p�~�ֶW�L�̤j�~��')
        return self.clean_data['min_age']
        

def splitData(strData,strToken=',|;| '):
    return [s.strip() for s in re.split(strToken,strData) if s.strip()]

 # save event into database
def processAddEvent(request):
    objUser,objVolunteer,objNpo=flowBase.verifyNpo(request)
    if not objNpo:
        return HttpResponseForbidden(u'���~���ާ@�y�{')

    # Fetch event input from request
    if request.method == 'POST' and request.POST.get('submitType'):
        submitType = request.POST.get('submitType')
        form = NewEventForm(data = request.POST)
        
        if form.is_valid():
            form.clean_data['npo_profile_ref']=objNpo
            form.clean_data['volunteer_profile_ref']=objVolunteer
            #form.clean_data['questionnaire_template_ref']=
            
            form.clean_data['status']='new application'
            form.clean_data['create_time']=datetime.datetime.now()
            form.clean_data['update_time']=datetime.datetime.now()
            #form.clean_data['questionnaire_template_id']=
            if form.clean_data['attachment_links_show']:
                form.clean_data['attachment_links']=[db.Link(form.clean_data['attachment_links_show'])]
            else:
                form.clean_data['attachment_links']=[]
            form.clean_data['npo_event_rating']=0
            form.clean_data['event_rating']=0

            newEventEntity = form.save(commit=False)
            # Check if some filed may become None due to no input
            if(None == newEventEntity.registration_fee):
                newEventEntity.registration_fee=0
            if(None == newEventEntity.expense):
                newEventEntity.expense=0
            if('' == newEventEntity.summary):
                newEventEntity.summary=None
            newEventEntity.status='new application'
            newEventEntity.put() 
                       
        # Save into datastore based on submit type
            if('send' == submitType):
                dic={'event_key':newEventEntity.key(),
                 'phone_number':''.join(objVolunteer.cellphone_no.split('-')),
                 'base': flowBase.getBase(request, 'npo'),
                 'page': 'event'}
                return render_to_response('event/event-sms-1.html', dic)
            else:
                return HttpResponseRedirect('listEvent')
    else:
        form = NewEventForm()
        
    dicData={'form': form,
             'base': flowBase.getBase(request,'npo'),
             'page': 'event'}
    return render_to_response('event/event-admin-add.html', dicData)

def processEditEvent(request):
    objUser,objVolunteer,objNpo=flowBase.verifyNpo(request)
    if not objNpo:
        return HttpResponseForbidden(u'���~���ާ@�y�{')
    
    if request.method != 'POST' or 'event_key' not in request.POST:
        return HttpResponseForbidden(u'���~���ާ@�y�{')

    eventKey = request.POST['event_key']
    eventProfile=db.get(db.Key(eventKey))
    if None == eventProfile:
        return HttpResponseForbidden(u'��Ƥ��s�b! key:%s'%eventKey)
    if eventProfile.npo_profile_ref.id!=objNpo.id:
        return HttpResponseForbidden(u'���~���ާ@�y�{')
    
    if 'submitType' in request.POST:
        submitType = request.POST['submitType']
        if not submitType:
            return HttpResponseForbidden(u'���~���ާ@�y�{')
        form = NewEventForm(data = request.POST , instance = eventProfile)
        if form.is_valid():
            modEventEntity = form.save(commit=False)
            if form.clean_data['attachment_links_show']:
                form.clean_data['attachment_links']=[db.Link(form.clean_data['attachment_links_show'])]
            else:
                form.clean_data['attachment_links']=[]
            # Check if some filed may become None due to no input
            if(None == modEventEntity.registration_fee):
                modEventEntity.registration_fee=0
                
            if(None == modEventEntity.expense):
                modEventEntity.expense=0
            
            if('' == modEventEntity.summary):
                modEventEntity.summary=None

            modEventEntity.status = 'new application'
            modEventEntity.put()
            if('send' == submitType):
                dic={'event_key':modEventEntity.key(),
                     'phone_number':''.join(objVolunteer.cellphone_no.split('-')),
                     'base': flowBase.getBase(request,'npo'),
                     'page': 'event'
                     }
                return render_to_response('event/event-sms-1.html', dic)
            return HttpResponseRedirect('listEvent')
    else:
        form = NewEventForm(instance = eventProfile)
    dic={'form':form, 'event_key':eventKey,
         'base':flowBase.getBase(request,'npo'),
         'page': 'event'}
    return render_to_response('event/event-admin-edit.html', dic)
    