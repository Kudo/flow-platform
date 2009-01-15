# -*- coding: UTF-8 -*-
import time
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import TemplateDoesNotExist
from db import ddl3
from google.appengine.ext import db
from datetime import datetime
from django import forms

class NewEventForm(forms.Form):
    txtActivityName = forms.CharField(label=u"活動名稱*",required=True,widget=forms.TextInput(attrs={'size':'37'}))
    txtStartDate = forms.DateTimeField(label=u"開始時間*",required=True,initial='2009-01-14',widget=forms.DateTimeInput(attrs={'size':'20'}))
    txtEndDate = forms.DateTimeField(label=u"結束時間*",required=True,initial='2009-01-14',widget=forms.DateTimeInput(attrs={'size':'20'}))
    txtPlace = forms.CharField(label=u"地點*",required=True,initial='Taipei',widget=forms.TextInput(attrs={'size':'59'}))
    txtVolunteerHour = forms.IntegerField(label=u"志工服務*",required=True,min_value=0,initial=1,widget=forms.TextInput(attrs={'size':'20'}))
    txtServiceTarget = forms.CharField(label=u"服務對象*",required=True,initial='B',widget=forms.TextInput(attrs={'size':'38'}))
    txtLabel = forms.CharField(label=u"標籤(關鍵字)*",required=True,initial='C',widget=forms.TextInput(attrs={'size':'20'}))
    txtOriginator = forms.CharField(label=u"發起人",required=False,widget=forms.TextInput(attrs={'size':'20'}))
    txtOrignatorGroup = forms.CharField(label=u"發起群組",required=False,widget=forms.TextInput(attrs={'size':'20'}))
    txtMobile0 = forms.CharField(label=u"連絡手機*",required=True,initial='0900000000',widget=forms.TextInput(attrs={'size':'21'}))
    txtActivityTarget = forms.CharField(label=u"活動目的*",required=True,initial='D',widget=forms.TextInput(attrs={'size':'49'}))
    txtActivityContent = forms.CharField(label=u"活動內容*",required=False,widget=forms.Textarea())
    txtActivityCost = forms.IntegerField(label=u"費用金額",required=False,widget=forms.TextInput(attrs={'size':'20'}))
    txtRegistrationFee = forms.IntegerField(label=u"報名費 ",required=False,widget=forms.TextInput(attrs={'size':'20'}))
    txtProjectProposalAddress = forms.URLField(label=u"活動企劃書位址*",required=True,initial='http://www.google.com.tw',widget=forms.TextInput(attrs={'size':'58'}))

 # save event into database
def processAddEvent(request):
              
    # Fetch event input from request
    if request.method == 'POST':
        
        submitType = request.POST['submitType']
    
        if('cancel' == submitType):
            return HttpResponseRedirect('listEvent')              # Because there is no activity_admin page now
        
        form = NewEventForm(request.POST)
        if form.is_valid():
        # Create New Activity Instance                       
            # Prepare some mock reference model and some required data
            npoRef = ddl3.NpoProfile.all().get()
            questionnaire_template_ref = ddl3.QuestionnaireTemplate.all().get()
            volunteer_profile_ref = ddl3.VolunteerProfile.all().get()
            tagValue = form.cleaned_data['txtLabel']
            tagList = [tagValue]           
            
            newEventDict = {            
            'event_name' : form.cleaned_data['txtActivityName'],
            'event_id' : str(int(time.time())),       # must 10 digital value
            'description' : 'UI not perform!!',
            'npo_profile_ref' : npoRef,
            'volunteer_profile_ref' : volunteer_profile_ref,
            'category' : 'TBD',
            'start_time' : form.cleaned_data['txtStartDate'],
            'end_time' : form.cleaned_data['txtEndDate'],
            'reg_start_time' : form.cleaned_data['txtStartDate'],
            'reg_end_time' : form.cleaned_data['txtEndDate'],
            'objective' : form.cleaned_data['txtActivityTarget'],
            'status' : 'new application',
            'max_age' : 90,
            'min_age' : 10,
            'questionnaire_template_ref' : questionnaire_template_ref,
            'event_rating' : 10,
            'npo_event_rating' : 10,
            'create_time' : datetime.now(),
            'update_time' : datetime.now(),
            'event_region': [form.cleaned_data['txtPlace']],
            'event_hours' : form.cleaned_data['txtVolunteerHour'],
            'event_target' : [form.cleaned_data['txtServiceTarget']],
            'tag' : tagList,
            'summary' : form.cleaned_data['txtActivityContent'],
            'attachment_links' : [db.Link(form.cleaned_data['txtProjectProposalAddress'])],
            'expense' : form.cleaned_data['txtActivityCost'],
            'registration_fee' : form.cleaned_data['txtRegistrationFee'],
            'event_zip' : ['104'],
            'event_field' : ['Computer'] 
            }            
            
            # Check if some filed may become None due to no input
            if(None == newEventDict.get('registration_fee')):
                newEventDict['registration_fee']=0
            
            if(None == newEventDict.get('expense')):
                newEventDict['expense']=0
            
            if('' == newEventDict.get('summary')):
                newEventDict['summary']=None
            
            newEventProfile = ddl3.EventProfile(**newEventDict)            
        
        
        # Save into datastore based on submit type
            if('send' == submitType):
                newEventProfile.status = 'approved'            
            
                        
            # Save into database
            newEventProfile.put() 
            return HttpResponseRedirect('listEvent')
    else:
        form = NewEventForm()   
    
    return render_to_response('event/event-admin-add.html', {'form': form})

# Modify Event
def modifyEvent(request):
    pass

# submit event to invest
def submitEvent(request):
   pass
    