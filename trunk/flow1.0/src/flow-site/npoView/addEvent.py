import time, re
from datetime import datetime
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from google.appengine.ext import db
from django import forms
from db import ddl

class NewEventForm(forms.Form):
    txtActivityName = forms.CharField(required=True,widget=forms.TextInput(attrs={'size':'37'}))
    description = forms.CharField(required=True,initial=u'event description',widget=forms.Textarea(attrs={'rows':'4', 'cols':'40'}))
    txtStartDate = forms.DateTimeField(required=True,initial=datetime.utcnow(),widget=forms.DateTimeInput(attrs={'size':'20'}))
    txtEndDate = forms.DateTimeField(required=True,initial=datetime.utcfromtimestamp(time.time()+86400),widget=forms.DateTimeInput(attrs={'size':'20'}))
    txtPlace = forms.CharField(required=True,initial='Taipei',widget=forms.TextInput(attrs={'size':'59'}))
    txtVolunteerHour = forms.IntegerField(required=True,min_value=0,initial=1,widget=forms.TextInput(attrs={'size':'20'}))
    txtServiceTarget = forms.CharField(required=True,initial='B',widget=forms.TextInput(attrs={'size':'38'}))
    txtLabel = forms.CharField(required=True,initial='C',widget=forms.TextInput(attrs={'size':'20'}))
    txtOriginator = forms.CharField(required=False,widget=forms.TextInput(attrs={'size':'20'}))
    txtOrignatorGroup = forms.CharField(required=False,widget=forms.TextInput(attrs={'size':'20'}))
    txtMobile0 = forms.CharField(required=True,initial='0900000000',widget=forms.TextInput(attrs={'size':'21'}))
    txtActivityTarget = forms.CharField(required=True,initial='D',widget=forms.TextInput(attrs={'size':'49'}))
    txtActivityContent = forms.CharField(required=True,initial=u'Content',widget=forms.Textarea())
    txtActivityCost = forms.IntegerField(required=False,widget=forms.TextInput(attrs={'size':'20'}))
    txtRegistrationFee = forms.IntegerField(required=False,widget=forms.TextInput(attrs={'size':'20'}))
    txtProjectProposalAddress = forms.URLField(required=True,initial='http://www.google.com.tw',widget=forms.TextInput(attrs={'size':'58'}))

def splitData(strData,strToken=',|;| '):
    return [s.strip() for s in re.split(strToken,strData) if s.strip()]

 # save event into database
def processAddEvent(request):
              
    # Fetch event input from request
    if request.method != 'POST':
        return HttpResponseRedirect('listEvent')
        
    submitType = request.POST['submitType']
    
    if(submitType=='cancel'):
        return HttpResponseRedirect('listEvent')
    if(submitType==''):
        form = NewEventForm()
    else:
        form = NewEventForm(request.POST)
        if form.is_valid():
        # Create New Activity Instance                       
            # Prepare some mock reference model and some required data
            npoRef = ddl.NpoProfile.all().get()
            questionnaire_template_ref = ddl.QuestionnaireTemplate.all().get()
            volunteer_profile_ref = ddl.VolunteerProfile.all().get()

            newEventDict = {            
            'event_name' : form.cleaned_data['txtActivityName'],
            'event_id' : str(int(time.time())),       # must 10 digital value
            'description' : form.cleaned_data['description'],
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
            'event_region': splitData(form.cleaned_data['txtPlace']),
            'event_hours' : form.cleaned_data['txtVolunteerHour'],
            'event_target' : [form.cleaned_data['txtServiceTarget']],
            'tag' : splitData(form.cleaned_data['txtLabel']),
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
            
            newEventProfile = ddl.EventProfile(**newEventDict)
        
        
        # Save into datastore based on submit type
            if('send' == submitType):
                newEventProfile.status = 'approved'
                newEventProfile.approved=True
                newEventProfile.approved_time=datetime.now()
            
                        
            # Save into database
            newEventProfile.put() 
            return HttpResponseRedirect('listEvent')
        
    
    return render_to_response('event/event-admin-add.html', {'form': form})

# Modify Event
def modifyEvent(request):
    pass

# submit event to invest
def submitEvent(request):
   pass
    
