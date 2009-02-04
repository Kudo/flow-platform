import time, re
from datetime import datetime
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from google.appengine.ext import db
from django import newforms as forms
from db import ddl
from google.appengine.ext.webapp import template
from google.appengine.ext.db import djangoforms

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
    

def splitData(strData,strToken=',|;| '):
    return [s.strip() for s in re.split(strToken,strData) if s.strip()]

 # save event into database
def processAddEvent(request):
              
    # Fetch event input from request
    if request.method == 'POST':
        submitType = request.POST.get('submitType')
        
        if(submitType=='cancel'):
            return HttpResponseRedirect('/npo/listEvent')
        
        if not submitType:
            form = NewEventForm()
        else:
            form = NewEventForm(data = request.POST)
            
            if form.is_valid():
                # Create New Activity Instance  
                npoRef = ddl.NpoProfile.all().get()
                questionnaire_template_ref = ddl.QuestionnaireTemplate.all().get()
                volunteer_profile_ref = ddl.VolunteerProfile.all().get()               
                
                
                form.clean_data['event_id']=str(int(time.time()))
                form.clean_data['npo_profile_ref']=npoRef
                form.clean_data['volunteer_profile_ref']=volunteer_profile_ref
                form.clean_data['questionnaire_template_ref']=questionnaire_template_ref
                
                form.clean_data['status']='new application'
                form.clean_data['create_time']=datetime.now()
                form.clean_data['update_time']=datetime.now()
                form.clean_data['questionnaire_template_id']=11111 # There is no questionnaire_template_ref.id (based on ddl.py) ??
                form.clean_data['attachment_links']=[db.Link(form.clean_data['attachment_links_show'])]
                form.clean_data['npo_event_rating']=0
                form.clean_data['event_rating']=0
                
                newEventEntity = form.save(commit=False)
                
                # Prepare some mock reference model and some required data
                
#===============================================================================
#                newEventEntity.volunteer_profile_ref = volunteer_profile_ref
#                newEventEntity.questionnaire_template_ref = questionnaire_template_ref
#                newEventEntity.npo_profile_ref = npo_profile_ref
#                newEventEntity.event_id = str(int(time.time()))
#                newEventEntity.status = 'new application'                             
#                newEventEntity.event_rating = 0                # System produce , set to 0 in beginning
#                newEventEntity.npo_event_rating = 0            # User produced?? , need to be calculated from VOLUNTEER_EVENT 
#                newEventEntity.create_time = datetime.now()
#                newEventEntity.update_time = datetime.now()
#                #newEventEntity.event_region = splitData(form.clean_data['event_region'])
#                #newEventEntity.tag = splitData(form.clean_data['tag'])
#                newEventEntity.questionnaire_template_id = 11111 # There is no questionnaire_template_ref.id (based on ddl.py) ??
#                newEventEntity.attachment_links = [form.cleaned_data['attachment_links_show']]
#===============================================================================
#===============================================================================
#                newEventDict = {            
#                'event_name' : form.clean_data['event_name'],
#                'event_id' : str(int(time.time())),       # must 10 digital value
#                'description' : form.clean_data['description'],
#                'npo_profile_ref' : npoRef,
#                'volunteer_profile_ref' : volunteer_profile_ref,
#                'category' : 'TBD',
#                'start_time' : form.clean_data['start_time'],
#                'end_time' : form.clean_data['end_time'],
#                'reg_start_time' : form.clean_data['start_time'],
#                'reg_end_time' : form.clean_data['end_time'],
#                'objective' : form.clean_data['objective'],
#                'status' : 'new application',
#                'max_age' : 90,
#                'min_age' : 10,
#                'questionnaire_template_ref' : questionnaire_template_ref,
#                'event_rating' : 10,
#                'npo_event_rating' : 10,
#                'create_time' : datetime.now(),
#                'update_time' : datetime.now(),
#                'event_region': splitData(form.clean_data['txtPlace']),
#                'event_hours' : form.clean_data['event_hours'],
#                'event_target' : [form.clean_data['event_target']],
#                'tag' : splitData(form.clean_data['tag']),
#                'summary' : form.clean_data['summary'],
#                'attachment_links' : [db.Link(form.clean_data['attachment_links'])],
#                'expense' : form.clean_data['expense'],
#                'registration_fee' : form.clean_data['registration_fee'],
#                'event_zip' : ['104'],
#                'event_field' : ['Computer'] 
#                }            
#===============================================================================
                
                # Check if some filed may become None due to no input
                if(None == newEventEntity.registration_fee):
                    newEventEntity.registration_fee=0
                
                if(None == newEventEntity.expense):
                    newEventEntity.expense=0
                
                if('' == newEventEntity.summary):
                    newEventEntity.summary=None
                
                           
            # Save into datastore based on submit type
                if('send' == submitType):
                    newEventEntity.status = 'approved'
                    newEventEntity.approved=True
                    newEventEntity.approved_time=datetime.now()
                
                
                            
                # Save into database
                newEventEntity.put() 
                return HttpResponseRedirect('/npo/listEvent')            
    else:
        form = NewEventForm()
        
    
    return render_to_response('event/event-admin-add.html', {'form': form})

# Modify Event
def modifyEvent(request):
    # If not POST Get Entity from Data store and transfer to NewEventForm
    # If POST , Use old entity and new Form input to form a new Form and do as addnewevent...
    if request.method == 'POST':
        if request.POST.has_key('submitType'):           
        
            submitType = request.POST['submitType']
            
            if(submitType=='cancel'):
                return HttpResponseRedirect('/npo/listEvent')
        
            if not submitType:
                return HttpResponseRedirect('/npo/listEvent')
            else:
            
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
                    return HttpResponseRedirect('/npo/listEvent')         
        
        else:
            event_id = request.POST['event_id']        
            eventProfile = ddl.EventProfile.gql("WHERE event_id = :1" , event_id).get()         # event_id should be unique
            
            if None == eventProfile:
                raise db.BadQueryError()
            
            form = NewEventForm(instance = eventProfile)
    
        return render_to_response('event/event-admin-edit.html', {'form': form,'event_id' : event_id})
    return HttpResponseRedirect('/npo/listEvent')

# submit event to invest
def submitEvent(request):
   pass
    
