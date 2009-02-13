from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import TemplateDoesNotExist
from google.appengine.ext import db
from db import ddl
from django import newforms as forms
import datetime

# Form submit verification
class volForm(forms.Form):
    approved = forms.CharField(required=False) # Field required

# Check to see if eventID is given. Direct to error page if not.
def volunteerShow(request):
    try:
        #strEventId = request.POST['event_id']
        strEventID = "2009010199"
    except KeyError:
        # Redirect to login page
        return render_to_response(r'someErrorPage.html', {})
    # Retrieve data with given eventID and status
    query = db.GqlQuery("SELECT * FROM VolunteerEvent WHERE event_id = :1 AND status = :2",strEventID,'approving')
    results = query.fetch(20)
    #print results[0].key
    #print strEventID
    return render_to_response(r'event\event-admin-validate.html', {'lstVolunteer' : addName(results)})


# append volunteer name from volunteer profile
def addName(lstVolEvent):
    '''
    Match and added correct rule to each activity according its status.
    @ return: active list with correct rule appended.
    '''
    lstVolID = []
    lstVolList = []
    # Retrieve all volunteer ID and put them in a list
    for volEvent in lstVolEvent:
        lstVolID.append(volEvent.volunteer_id)
    # select volunteer profile for the list of IDs given
    query = db.GqlQuery("SELECT * FROM VolunteerProfile WHERE volunteer_id = :1",lstVolID)
    results = query.fetch(20)
    #print volEvent.volunteer_id
    return results

def volSubmit(request):
    if request.method == 'POST': # If the form has been submitted...
        form = volForm(request.POST) # A form bound to the POST data
        print form.cleaned_data['approved']
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
    

