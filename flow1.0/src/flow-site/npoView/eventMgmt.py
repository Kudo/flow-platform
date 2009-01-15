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

def mainPage(request):
    # Retrieve Events from Database
    print request.POST
    query = db.GqlQuery("SELECT * FROM EventProfile")
    results = query.fetch(100)
    return render_to_response(r'event/event-admin-list.html', {'lstActivityList' : actionCheck(results)})

def actionCheck(lstEvent):
    '''
    Match and added correct rule to each activity according its status.
    @ return: active list with correct rule appended.
    '''
    lstActList = []
    
    for event in lstEvent:
        lstActList.append({"event_id":event.event_id,"name":event.event_name,"status":event.status,"dicPerm":dicRule[event.status]})
    return lstActList