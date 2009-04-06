import datetime
import random
from django.shortcuts import render_to_response
from db.ddl import VolunteerProfile, NpoProfile, EventProfile
import flowBase

displayEventCount = 5
displayExpertiseCount = 5

def home(request):
    now = datetime.datetime.now()

    tmpList = VolunteerProfile.all().order('-id').fetch(10)
    count = len(tmpList)
    if count <= 0:
        volunteer = None
    else:
        randomIndex = random.randint(0, count - 1)
        volunteerObj = tmpList[randomIndex]
        volunteerObj.showExpertise = u', '.join(volunteerObj.expertise[:displayExpertiseCount])
        if (len(volunteerObj.expertise) > displayExpertiseCount):
            volunteerObj.showExpertise += u', ...'
        volunteer = {
            'nickname':         volunteerObj.nickname,
            'region':           volunteerObj.resident_city,
            'showExpertise':    volunteerObj.showExpertise,
            'logo':             volunteerObj.logo,
            'key':              volunteerObj.key(),
        }
        del randomIndex, volunteerObj

    tmpList = NpoProfile.all().order('-id').fetch(10)
    count = len(tmpList)
    if count <= 0:
        npo = None
    else:
        randomIndex = random.randint(0, count - 1)
        npoObj = tmpList[randomIndex]
        npo = {
            'name':             npoObj.npo_name,
            'region':           npoObj.service_region,
            'description':      npoObj.brief_intro,
            'npo_id':           npoObj.npo_id,
            'logo':             npoObj.logo,
        }
        del randomIndex, npoObj
        
    del tmpList, count

    eventList = []
    for event in EventProfile.all().filter('status in ', ['approved', 'registrating']).order('-create_time').fetch(displayEventCount):
        if event.start_time > now:
            eventList.append({
                'eventKey':     str(event.key()),
                'name':         event.event_name,
                'npoName':      event.npo_profile_ref.npo_name,
                'npo_id':       event.npo_profile_ref.npo_id,
                'region':       u','.join(event.event_region),
                'startTime':    event.start_time.strftime('%Y-%m-%d %H:%M'),
                'description':  event.description,
            })

    template_values = {
            'base':                     flowBase.getBase(request),
            'volunteer':                volunteer,
            'npo':                      npo,
            'eventList':                eventList,
    }
    
    return render_to_response('homepage.html', template_values)
