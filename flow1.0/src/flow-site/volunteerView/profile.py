#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import cgi
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from google.appengine.ext import db
from google.appengine.api import users
import flowBase
from db.ddl import VolunteerProfile, VolunteerIm

def show(request):
    if 'volunteer_id' not in request.GET:
        if users.get_current_user():
            userID = users.get_current_user()
            isSelf = True
        else:
            return HttpResponseRedirect('/')
    else:
        userID = cgi.escape(request.GET['volunteer_id'])
        if userID.find('@gmail.com') == -1:
            userID += '@gmail.com'
            userID = users.User(userID)
            isSelf = True if users.get_current_user() == userID else False

    user = db.GqlQuery('SELECT * FROM VolunteerProfile WHERE volunteer_id = :1', userID).get()
    if not user:
        pass
    userIM = user.im2volunteer.get()
    template_values = {
            'isSelf':                   isSelf,
            'base':                     flowBase.getBase(request, user),
            'sex':                      user.sex,
            'cellphone_no':             (user.cellphone_no or '無') if isSelf or not user.hide_cellphone else '******',
            'blog':                     user.blog,
            'email':                    re.sub('(.+)@(.+)', '\\1 (at) \\2', user.gmail),
            'im':                       '%s：%s' % ( userIM.im_type, userIM.im_account.address) if userIM else '無',
            'brief_intro':              user.brief_intro or '無',

    }
    response = render_to_response('volunteer/profile_info.html', template_values)

    return response


def edit(request):
    if not users.get_current_user():
        return HttpResponseRedirect('profile')

    user = db.GqlQuery('SELECT * FROM VolunteerProfile WHERE volunteer_id = :1', users.get_current_user()).get()
    if not user:
        pass
    userIM = user.im2volunteer.get()
    if request.method == 'POST':
        try:
            (user.volunteer_first_name, user.volunteer_last_name) = request.POST['name'].split(None, 1)
        except:
            (user.volunteer_first_name, user.volunteer_last_name) = (request.POST['name'][0], request.POST['name'][1:])
        user.cellphone_no = request.POST['cellphone_no']
        user.put()
        return HttpResponseRedirect('/volunteer/profile')
    else:
        template_values = {
                'base':                     flowBase.getBase(request, user),
                'selfLink':                 request.path,
                'sex':                      user.sex,
                'email':                    user.gmail,
                'im':                       '%s：%s' % ( userIM.im_type, userIM.im_account.address) if userIM else '無',
                'cellphone_no':             user.cellphone_no,
                'blog':                     user.blog,
                'brief_intro':              user.brief_intro or '無',
        }
        response = render_to_response('volunteer/profile_edit.html', template_values)
        return response
