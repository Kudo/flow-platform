#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
        user = db.GqlQuery('SELECT * FROM VolunteerProfile WHERE volunteer_id = :1', users.User(request.GET['volunteer_id']+'@gmail.com')).get()
        mySelf = db.GqlQuery('SELECT * FROM VolunteerProfile WHERE volunteer_id = :1', mySelf).get()
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
        user = db.GqlQuery('SELECT * FROM VolunteerProfile WHERE volunteer_id = :1', users.User(request.GET['volunteer_id']+'@gmail.com')).get()
        mySelf = db.GqlQuery('SELECT * FROM VolunteerProfile WHERE volunteer_id = :1', mySelf).get()
        mySelf.friends.remove(user.key())
        mySelf.put()
    except:
        return HttpResponse(simplejson.dumps({'statusCode': 404, 'reason': str(sys.exc_info())}), mimetype='application/json')
    return HttpResponse(simplejson.dumps({'statusCode': 200, 'reason': 'success'}), mimetype='application/json')


def show(request):
    mySelf = users.get_current_user()
    if not mySelf:
        return HttpResponseRedirect('/')

    user = db.GqlQuery('SELECT * FROM VolunteerProfile WHERE volunteer_id = :1', mySelf).get()
    if not user:
        pass

    friends = [VolunteerProfile.get(user.friends[i]) for i in range(0, 10) if i < len(user.friends)]
    template_values = {
            'base':                     flowBase.getBase(request, user),
            'friends':                  friends,
            'firstFriend':              friends[0],
            'test':                     range(20),
    }

    response = render_to_response('volunteer/profile_friends.html', template_values)
    return response
