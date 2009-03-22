#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cgi
import sys
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.utils import simplejson
from google.appengine.ext import db
from google.appengine.api import users
import flowBase
from db.ddl import VolunteerProfile, VolunteerIm

def create(request):
    mySelf = users.get_current_user()
    if 'volunteer_id' not in request.GET or not mySelf:
        return HttpResponse(simplejson.dumps({'statusCode': 404, 'reason': 'No login'}), mimetype='application/json')
    if mySelf.nickname() == request.GET['volunteer_id']:
        return HttpResponse(simplejson.dumps({'statusCode': 405, 'reason': 'Adding yourself as friend'}), mimetype='application/json')
    try:
        user = flowBase.getVolunteer(cgi.escape(request.GET['volunteer_id'])+'@gmail.com')
        mySelf = flowBase.getVolunteer(mySelf)
        if user.key() not in mySelf.friends:
            mySelf.friends.append(user.key())
            mySelf.put()
        else:
            return HttpResponse(simplejson.dumps({'statusCode': 401, 'reason': 'Already friend'}), mimetype='application/json')
    except:
        return HttpResponse(simplejson.dumps({'statusCode': 404, 'reason': str(sys.exc_info())}), mimetype='application/json')
    return HttpResponse(simplejson.dumps({'statusCode': 200, 'reason': 'success'}), mimetype='application/json')


def delete(request):
    mySelf = users.get_current_user()
    if 'volunteer_id' not in request.GET or not mySelf:
        return HttpResponse(simplejson.dumps({'statusCode': 404, 'reason': 'No login'}), mimetype='application/json')
    try:
        user = flowBase.getVolunteer(cgi.escape(request.GET['volunteer_id'])+'@gmail.com')
        mySelf = flowBase.getVolunteer(mySelf)
        mySelf.friends.remove(user.key())
        mySelf.put()
    except:
        return HttpResponse(simplejson.dumps({'statusCode': 404, 'reason': str(sys.exc_info())}), mimetype='application/json')
    return HttpResponse(simplejson.dumps({'statusCode': 200, 'reason': 'success'}), mimetype='application/json')


def show(request):
    base = flowBase.getBase(request)
    volunteer = flowBase.getVolunteer(base['user'])
    if not volunteer:
        return HttpResponseRedirect('/')

    friends = [VolunteerProfile.get(volunteer.friends[i]) for i in range(0, 10) if i < len(volunteer.friends)]
    template_values = {
            'base':                     base,
            'volunteerBase':            flowBase.getVolunteerBase(volunteer),
            'friends':                  friends,
            'firstFriend':              friends[0] if len(friends) > 0 else None,
            'test':                     range(20),
    }

    response = render_to_response('volunteer/profile_friends.html', template_values)
    return response
