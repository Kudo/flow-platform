import time, re
from datetime import datetime
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from google.appengine.ext import db
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
        event_fields = ['event_name', 'description', 'start_time', 'end_time','reg_start_time','reg_end_time', 'event_region', 'event_hours', 'event_target', 'tag', 'objective', 'summary', 'expense','registration_fee','attachment_links_show','event_zip','event_field','category']
        volunteer_fileds = ['sex','max_age', 'min_age','volunteer_req','expertise_req','join_flow_plan']
        event_feedback_fileds = ['event_album_link','event_video_link','event_blog_link','sentiments']
        model = ddl.EventProfile
        fields = event_fields + volunteer_fileds + event_feedback_fileds        
    

# Modify Event
def processEditEvent(request):
    # If not POST Get Entity from Data store and transfer to NewEventForm
    # If POST , Use old entity and new Form input to form a new Form and do as addnewevent...
    if request.method != 'POST':
        return HttpResponseRedirect('/npo/')
    
    if request.POST.has_key('submitType'):           
    
        submitType = request.POST['submitType']
    
        if not submitType:
            return HttpResponseRedirect('/npo/')

        event_id = request.POST['event_id']        
        eventProfile = ddl.EventProfile.gql("WHERE event_id = :1" , event_id).get()         # event_id should be unique
        
        if None == eventProfile:
            raise db.BadQueryError()
        
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
                           
            # Save into datastore based on submit type
            if('send' == submitType):
                modEventEntity.status = 'approved'
                modEventEntity.approved=True
                modEventEntity.approved_time=datetime.now()
            
            if('save' == submitType):
                modEventEntity.status = 'new application'
                modEventEntity.approved=False
                modEventEntity.approved_time=None

            # Save into database
            modEventEntity.put() 
            return HttpResponseRedirect('/npo/')
    
    else:
        event_id = request.POST['event_id']        
        eventProfile = ddl.EventProfile.gql("WHERE event_id = :1" , event_id).get()         # event_id should be unique
        
        if None == eventProfile:
            raise db.BadQueryError()
        
        form = NewEventForm(instance = eventProfile)

    return render_to_response('event/event-admin-edit.html', {'form':form, 'event_id':event_id, 'base':flowBase.getBase(request)})
    
