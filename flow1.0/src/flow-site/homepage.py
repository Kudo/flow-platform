import datetime
import random
from django.shortcuts import render_to_response
from db.ddl import VolunteerProfile, NpoProfile, EventProfile
import flowBase

displayEventCount = 5

def home(request):
    now = datetime.datetime.now()

    tmpList = VolunteerProfile.all().order('-id').fetch(10)
    count = len(tmpList)
    randomIndex = random.randint(0, count - 1)
    volunteer = tmpList[randomIndex]

    tmpList = NpoProfile.all().order('-id').fetch(10)
    count = len(tmpList)
    randomIndex = random.randint(0, count - 1)
    npo = tmpList[randomIndex]

    del tmpList, count, randomIndex

    eventList = []
    for event in EventProfile.all().filter('status in ', ['approved', 'recruiting']).order('-create_time').fetch(displayEventCount):
        if event.start_time > now:
            eventList.append({
                'eventKey': str(event.key()),
                'name': event.event_name,
                'npoName': event.npo_profile_ref.npo_name,
                'region': u','.join(event.event_region),
                'startTime': event.start_time.strftime('%Y-%m-%d %H:%M'),
                'description': event.description,
            })

    template_values = {
            'base':                     flowBase.getBase(request),
            'volunteer':                volunteer,
            'npo':                      npo,
            'eventList':                eventList,
    }
    
    return render_to_response('homepage.html', template_values)
