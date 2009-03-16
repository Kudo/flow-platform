import time, re
from datetime import datetime
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from google.appengine.ext import db
from google.appengine.api import users
from django import newforms as forms
from db import ddl
from google.appengine.ext.db import djangoforms
import flowBase

class NewEventForm(djangoforms.ModelForm):
    event_name = forms.CharField(required=True,widget=forms.TextInput(attrs={'size':'37'}))
    description = forms.CharField(required=True,initial=u'event description',widget=forms.Textarea(attrs={'rows':'4', 'cols':'40'}))
    start_time = forms.DateTimeField(required=True,initial=str(datetime.now())[:16],widget=forms.TextInput(attrs={'size':'20'}))
    end_time = forms.DateTimeField(required=True,initial=str(datetime.fromtimestamp(time.time()+86400))[:16],widget=forms.TextInput(attrs={'size':'20'}))
    reg_start_time = forms.DateTimeField(required=True,initial=str(datetime.now())[:16],widget=forms.TextInput(attrs={'size':'20'}))
    reg_end_time = forms.DateTimeField(required=True,initial=str(datetime.now())[:16],widget=forms.TextInput(attrs={'size':'20'}))
    #event_region = forms.CharField(required=True,initial='Taipei',widget=forms.TextInput(attrs={'size':'59'}))
    event_hours = forms.IntegerField(required=True,min_value=0,initial=1,widget=forms.TextInput(attrs={'size':'20'}))
    event_target = forms.CharField(required=True,initial='',widget=forms.TextInput(attrs={'size':'38'}))    
    objective = forms.CharField(required=True,initial='',widget=forms.TextInput(attrs={'size':'49'}))
    summary = forms.CharField(required=False,initial=u'Event content',widget=forms.Textarea(attrs={'rows':'4', 'cols':'40'}))
    expense = forms.IntegerField(required=False,widget=forms.TextInput(attrs={'size':'20'}))
    registration_fee = forms.IntegerField(required=False,widget=forms.TextInput(attrs={'size':'20'}))
    attachment_links_show = forms.URLField(required=False,initial='http://www.google.com.tw',widget=forms.TextInput(attrs={'size':'58'}))
    
    max_age = forms.IntegerField(required=True,min_value=1,initial=99,widget=forms.TextInput(attrs={'size':'3'}))
    min_age = forms.IntegerField(required=True,min_value=1,initial=1,widget=forms.TextInput(attrs={'size':'3'}))    
    volunteer_req = forms.IntegerField(required=True,min_value=1,initial=1,widget=forms.TextInput(attrs={'size':'3'}))
    
   
    class Meta:
        event_fields = ['event_name', 'description', 'start_time', 'end_time','reg_start_time','reg_end_time',
                        'event_region', 'event_hours', 'event_target', 'tag', 'objective', 'summary', 'expense',
                        'registration_fee','attachment_links_show','event_zip','event_field','category']
        volunteer_fileds = ['sex','max_age', 'min_age','volunteer_req','expertise_req','join_flow_plan']
        event_feedback_fileds = ['event_album_link','event_video_link','event_blog_link','sentiments']
        model = ddl.EventProfile
        fields = event_fields + volunteer_fileds + event_feedback_fileds        
    

def splitData(strData,strToken=',|;| '):
    return [s.strip() for s in re.split(strToken,strData) if s.strip()]

 # save event into database
def processAddEvent(request):
    objUser=users.get_current_user()
    if not objUser:
        return HttpResponseRedirect('/')
    objVolunteer=flowBase.getVolunteer(objUser)
    if not objVolunteer:
        return HttpResponseRedirect('/')
    objNpo=flowBase.getNpoByUser(objUser)
    if not objNpo:
        return HttpResponseRedirect('/')

    # Fetch event input from request
    if request.method == 'POST' and request.POST.get('submitType'):
        submitType = request.POST.get('submitType')
        form = NewEventForm(data = request.POST)
        
        if form.is_valid():
            # Create New Activity Instance  
            form.clean_data['npo_profile_ref']=objNpo
            form.clean_data['volunteer_profile_ref']=objVolunteer
            #form.clean_data['questionnaire_template_ref']=
            
            form.clean_data['status']='new application'
            form.clean_data['create_time']=datetime.now()
            form.clean_data['update_time']=datetime.now()
            #form.clean_data['questionnaire_template_id']=
            form.clean_data['attachment_links']=[db.Link(form.clean_data['attachment_links_show'])]
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
        
    
    return render_to_response('event/event-admin-add.html', {'form': form, 'base': flowBase.getBase(request,'npo'),'page': 'event'})


# submit event to invest
def submitEvent(request):
   pass
    