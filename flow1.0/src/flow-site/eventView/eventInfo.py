from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import TemplateDoesNotExist
from google.appengine.ext import db
from db import ddl3

dicRule = {'new application'        :{'modify':'','recruit':'disabled','validate':'disabled','close':'disabled','cancel':''},
           'approved'               :{'modify':'','recruit':'disabled','validate':'disabled','close':'disabled','cancel':''},
           'announced'              :{'modify':'','recruit':'disabled','validate':'disabled','close':'disabled','cancel':''},
           'authenticating'         :{'modify':'','recruit':'disabled','validate':'disabled','close':'disabled','cancel':''},
           'authenticated'          :{'modify':'','recruit':'','validate':'','close':'disabled','cancel':''},
           'registrating'           :{'modify':'','recruit':'','validate':'','close':'disabled','cancel':''},
           'recruiting'             :{'modify':'','recruit':'','validate':'','close':'disabled','cancel':''},
           'registration closed'    :{'modify':'','recruit':'disabled','validate':'disabled','close':'disabled','cancel':'disabled'},
           'on-going'               :{'modify':'','recruit':'','validate':'','close':'disabled','cancel':'disabled'},
           'filling polls'          :{'modify':'','recruit':'disabled','validate':'disabled','close':'disabled','cancel':'disabled'},
           'activity closed'        :{'modify':'disabled','recruit':'disabled','validate':'disabled','close':'','cancel':'disabled'},
           'case-closed reporting'  :{'modify':'disabled','recruit':'disabled','validate':'disabled','close':'disabled','cancel':'disabled'},
           'cancelled'              :{'modify':'disabled','recruit':'disabled','validate':'disabled','close':'disabled','cancel':'disabled'},
           'abusive usage'          :{'modify':'disabled','recruit':'disabled','validate':'disabled','close':'disabled','cancel':'disabled'}
           }
def showEvent(request):
    # Retrieve Events from Database
    eventKey=request.GET.get('id')
    event=db.get(db.Key(eventKey))
    dicData={"originator":event.originator,"create_time":event.create_time,"category":event.category,
        "event_region":event.event_region,"event_target":event.event_target,"event_hours":event.event_hours,
        "summary":event.summary,"event_id":event.event_id}
    return render_to_response(r'event\event-info.html', {'event' : dicData})
