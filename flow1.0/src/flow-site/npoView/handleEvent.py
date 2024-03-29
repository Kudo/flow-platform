# -*- coding: big5 -*-
import time, re, datetime,logging
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render_to_response
from google.appengine.ext import db
from google.appengine.api import users
from django import newforms as forms
from db import ddl
from google.appengine.ext.db import djangoforms
from common.widgets import FlowSplitDateTimeWidget,FlowExpertiseChoiceWidget,ListTextInput
from common.fields import FlowChoiceField,ListURLField
import flowBase

g_lstRegion=[(s,s) for s in flowBase.getRegion()]
g_lstRegion.insert(0,('',u'請選擇...'))
g_lstExpertise = [(s.encode('UTF-8'), s) for s in flowBase.getProfessionList()]

class NewEventForm(djangoforms.ModelForm):
    event_name = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'size':'37'}))
    description = forms.CharField(max_length=50, widget=forms.Textarea(attrs={'rows':'4', 'cols':'40'}))
    start_time = forms.SplitDateTimeField(widget=FlowSplitDateTimeWidget())
    end_time = forms.SplitDateTimeField(widget=FlowSplitDateTimeWidget())
    reg_start_time = forms.SplitDateTimeField(widget=FlowSplitDateTimeWidget())
    reg_end_time = forms.SplitDateTimeField(widget=FlowSplitDateTimeWidget())
    event_region = FlowChoiceField(choices=g_lstRegion,widget=forms.Select())
    event_hours = forms.IntegerField(min_value=1,max_value=3600,initial=1,widget=forms.TextInput(attrs={'size':'5'}))
    summary = forms.CharField(required=False,widget=forms.Textarea(attrs={'rows':'4', 'cols':'40'}))
    registration_fee = forms.IntegerField(required=False,max_value=0x7fffffff, min_value=0,widget=forms.TextInput(attrs={'size':'20'}))
    attachment_links = ListURLField(required=False,initial='',widget=ListTextInput(attrs={'size':'60'}))
    min_age = forms.IntegerField(min_value=1,max_value=100,initial=1,widget=forms.TextInput(attrs={'size':'3'}))
    max_age = forms.IntegerField(min_value=1,max_value=100,initial=99,widget=forms.TextInput(attrs={'size':'3'}))
    volunteer_req = forms.IntegerField(min_value=1,max_value=10000,initial=1,widget=forms.TextInput(attrs={'size':'3'}))
    
    expertise_req = forms.MultipleChoiceField(required=False,choices=g_lstExpertise, widget=FlowExpertiseChoiceWidget())

    sex = FlowChoiceField(choices=[('Both',u'皆可'),('Male',u'男'),('Female',u'女')],widget=forms.Select())
    class Meta:
        event_fields = ['event_name', 'description', 'start_time','end_time','reg_start_time','reg_end_time',
                        'event_region', 'event_hours', 'tag', 'summary',
                        'registration_fee','attachment_links']
        volunteer_fileds = ['sex','max_age', 'min_age','volunteer_req','expertise_req']
        model = ddl.EventProfile
        fields = event_fields + volunteer_fileds
    
    def clean_start_time(self):
        if self.clean_data['start_time']<datetime.datetime.utcnow():
            raise forms.ValidationError(u'請輸入正確的開始時間')
        return self.clean_data['start_time']
        
    def clean_end_time(self):
        if self.clean_data['end_time']<datetime.datetime.utcnow():
            raise forms.ValidationError(u'請輸入正確的結束時間')
        if self.clean_data['end_time']<=self.clean_data['start_time']:
            raise forms.ValidationError(u'開始時間大於結束時間')
        return self.clean_data['end_time']
    def clean_reg_end_time(self):
        if self.clean_data['reg_end_time']>self.clean_data['start_time']:
            raise forms.ValidationError(u'報名截止時間超過活動開始時間')
        if self.clean_data['reg_end_time']<datetime.datetime.utcnow():
            raise forms.ValidationError(u'請輸入正確的結束時間')
        if self.clean_data['reg_end_time']<=self.clean_data['reg_start_time']:
            raise forms.ValidationError(u'開始時間大於結束時間')
        return self.clean_data['reg_end_time']
    def clean_max_age(self):
        if 'minx_age' in self.clean_data:
            if self.clean_data['max_age']<self.clean_data['min_age']:
                raise forms.ValidationError(u'最小年齡超過最大年齡')
        return self.clean_data['max_age']
    def clean_min_age(self):
        if 'max_age' in self.clean_data:
            if self.clean_data['max_age']<self.clean_data['min_age']:
                raise forms.ValidationError(u'最小年齡超過最大年齡')
        return self.clean_data['min_age']

def splitData(strData,strToken=',|;| '):
    return [s.strip() for s in re.split(strToken,strData) if s.strip()]

 # save event into database
def processAddEvent(request,npoid):
    objUser,objVolunteer,objNpo=flowBase.verifyNpo(request,npoid)
    if not objNpo:
        raise AssertionError("objNpo is None")

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
                return HttpResponseRedirect('/npo/%s/admin/authEvent1?event_key=%s'%(npoid,newEventEntity.key()))
            else:
                return HttpResponseRedirect('/npo/%s/admin/listEvent'%npoid)

    else:
        form = NewEventForm()
        
    dicData={'form': form,
             'formErrors':form.non_field_errors(),
             'base': flowBase.getBase(request,'npo'),
             'npoProfile': objNpo,
             'page': 'event'}
    return render_to_response('event/event-admin-add.html', dicData)

def processEditEvent(request,npoid):
    objUser,objVolunteer,objNpo=flowBase.verifyNpo(request,npoid)
    if not objNpo:
        raise AssertionError("objNpo is None")
    
    if request.method != 'POST' or 'event_key' not in request.POST:
        raise AssertionError("request.method != 'POST' or 'event_key' not in request.POST")

    eventKey = request.POST['event_key']
    eventProfile=db.get(db.Key(eventKey))
    if None == eventProfile:
        raise AssertionError('eventProfile is None')
    if eventProfile.npo_profile_ref.id!=objNpo.id:
        raise AssertionError('eventProfile.npo_profile_ref.id!=objNpo.id')
    
    if 'submitType' in request.POST:
        submitType = request.POST['submitType']
        if not submitType:
            raise AssertionError('submitType is None')
        form = NewEventForm(data = request.POST , instance = eventProfile)
        if form.is_valid():
            modEventEntity = form.save(commit=False)
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
                return HttpResponseRedirect('/npo/%s/admin/authEvent1?event_key=%s'%(npoid,modEventEntity.key()))
            return HttpResponseRedirect('/npo/%s/admin/listEvent'%npoid)
    else:
        form = NewEventForm(instance = eventProfile)
    dic={'form':form, 'event_key':eventKey,
         'formErrors':form.non_field_errors(),
         'base':flowBase.getBase(request,'npo'),
         'npoProfile': objNpo,
         'page': 'event'}
    return render_to_response('event/event-admin-edit.html', dic)
    
