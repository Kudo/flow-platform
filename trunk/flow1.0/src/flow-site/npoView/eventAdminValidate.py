import datetime
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import TemplateDoesNotExist
from google.appengine.ext import db
from db import ddl
from django import newforms as forms
import flowBase

# Form submit verification
class volForm(forms.Form):
    approved = forms.CharField(required=False) # Field required

# Check to see if eventID is given. Direct to error page if not.
def volunteerShow(request):
    try:
        strEventKey = request.POST['event_key']
    except KeyError:
        # Redirect to login page
        return HttpResponseRedirect('/npo/listEvent')
    event=db.get(db.Key(strEventKey))
    # Retrieve data with given eventID and status
    query = db.GqlQuery("SELECT * FROM VolunteerEvent WHERE event_profile_ref = :1 AND status = :2",event,'new registration')
    result1 = query.fetch(100)
    query = db.GqlQuery("SELECT * FROM VolunteerEvent WHERE event_profile_ref = :1 AND status = :2",event,'approved')
    result2 = query.fetch(100)
    dicData={'lstVolunteer' : addName(result1),
             'lstApproved' : addName(result2),
             'base':flowBase.getBase(request),
             'event':event
             }
    return render_to_response(r'event/event-admin-validate.html', dicData)

# append volunteer name from volunteer profile
def addName(lstVolEvent):
    '''
    Match and added correct rule to each activity according its status.
    @ return: active list with correct rule appended.
    '''
    # Retrieve all volunteer ID and put them in a list
    lstVolunteer=[]
    for volEvent in lstVolEvent:
        objVolunteer = db.GqlQuery("SELECT * FROM VolunteerProfile WHERE volunteer_id = :1",volEvent.volunteer_id).get()
        if objVolunteer:
            lstVolunteer.append(objVolunteer)
        else:
            raise RuntimeError('%s does NOT exist!'%volEvent.volunteer_id)
    return lstVolunteer

def volSubmit(request):
    if request.method == 'POST': # If the form has been submitted...
        form = volForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            lstApprovedVol = form.cleaned_data['approved']
            for approvedVol in lstApprovedVol:
                vol = ddl.VolunteerEvent(status='approved',approved_time=datetime.datetime.utcnow(),
                                                  volunteer_id=approvedVol.volunteer_id)
                vol.put()
            return HttpResponseRedirect(r'Apporved!!!') # Redirect after processed
    else:
        return render_to_response('SomeErrorLandingPage', {'form': form,})
    

