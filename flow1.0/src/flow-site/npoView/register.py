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
from db.ddl import NpoProfile, CountryCity
from itertools import chain
from django.conf import settings
from google.appengine.ext.webapp import template
try:
    from django import newforms as forms
except ImportError:
    from django import forms
from google.appengine.ext.db import djangoforms

class NpoProfileForm(djangoforms.ModelForm):
    npo_name                    = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'field text medium'}))
    founder                     = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'field text medium'}))
    brief_intro                 = forms.CharField(widget=forms.Textarea(attrs={'class': 'field textarea medium', 'cols': '50', 'rows': '10'}))
    logo                        = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'field text large'}))

    choices = []
    citys = db.GqlQuery('SELECT * FROM CountryCity WHERE state_en = :1', 'Taiwan').fetch(50)
    for city in citys:
        choices.append((city.city_en, city.city_tc))
    del citys
    service_region              = forms.ChoiceField(choices=choices, widget=forms.Select(attrs={'class': 'field select'}))

    service_target              = forms.CharField(widget=forms.TextInput(attrs={'class': 'field text medium'}))
    service_field               = forms.CharField(widget=forms.TextInput(attrs={'class': 'field text medium'}))
    contact                     = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'field text medium'}))
    website                     = forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={'class': 'field text', 'size': '50'}))
    blog                        = forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={'class': 'field text', 'size': '50'}))
    telephone                   = forms.CharField(max_length=20,  widget=forms.TextInput(attrs={'class': 'field text medium'}))
    fax                         = forms.CharField(max_length=20,  required=False, widget=forms.TextInput(attrs={'class': 'field text medium'}))

    foundyear                   = forms.CharField(required=False, min_length=4, max_length=4, widget=forms.TextInput(attrs={'class': 'field text', 'size': '4'}))
    foundmonth                  = forms.CharField(required=False, min_length=1, max_length=2, widget=forms.TextInput(attrs={'class': 'field text', 'size': '2'}))
    foundday                    = forms.CharField(required=False, min_length=1, max_length=2, widget=forms.TextInput(attrs={'class': 'field text', 'size': '2'}))

    authority                   = forms.CharField(required=False, initial='無', widget=forms.TextInput(attrs={'class': 'field text medium'}))
    bank_acct_no                = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'field text medium'}))
    bank_acct_name              = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'field text medium'}))

    class Meta:
        model = NpoProfile
        fields = ['npo_name', 'founder', 'brief_intro', 'logo',
                  'service_region', 'service_target', 'service_field',
                  'website', 'blog', 'founding_date', 'authority', 'bank_acct_no', 'bank_acct_name',
                 ]

def step1(request):
    user = users.get_current_user()
    if not flowBase.getVolunteer(user):
        pass
    if db.GqlQuery('SELECT * From NpoProfile WHERE founder = :1', user).count() > 0:
        pass
    if 'yes' in request.GET:
        return HttpResponseRedirect('/npo/register/step2/')
    if 'no' in request.GET:
        return HttpResponseRedirect('/')
    template_values = {
            'base':                     flowBase.getBase(request),
    }
    return render_to_response('registration/npo_step1.html', template_values)

def step2(request):
    if not flowBase.getVolunteer(users.get_current_user()):
        pass
    if 'register' in request.GET:
        return HttpResponseRedirect('/npo/register/step3/')
    template_values = {
            'base':                     flowBase.getBase(request),
    }
    return render_to_response('registration/npo_step2.html', template_values)

def step3(request):
    isWarning = None
    if 'registered' in request.GET:
        isWarning = u'這個 NPO 名稱已經被註冊了，請試著以其他名稱註冊。'
    user = flowBase.getVolunteer(users.get_current_user())
    if not user:
        pass

    if request.method != 'POST':
        form = NpoProfileForm()
    else:
        form = NpoProfileForm(data=request.POST)
        if not form.is_valid():
            isWarning = u'請檢查是否有資料輸入錯誤。'
        else:
            import datetime
            now = datetime.datetime.utcnow()
            cleaned_data = form._cleaned_data()
            service_region = db.GqlQuery('SELECT * From CountryCity WHERE city_en = :1', cleaned_data['service_region']).get().city_tc
            npoObj = NpoProfile(
                    google_acct                 = user,
                    create_time                 = now,
                    update_time                 = now,
                    status                      = "normal",
                    valid_google_acct           = True,

                    npo_name                    = cleaned_data['npo_name'],
                    founder                     = cleaned_data['founder'],
                    brief_intro                 = cleaned_data['brief_intro'],
                    logo                        = cleaned_data['logo'] or None,
                    service_region              = [service_region],
                    service_target              = [cleaned_data['service_target']],
                    service_field               = [cleaned_data['service_field']],
                    website                     = cleaned_data['website'],
                    blog                        = cleaned_data['blog'],
                    founding_date               = datetime.date(int(cleaned_data['foundyear']), int(cleaned_data['foundmonth']), int(cleaned_data['foundday'])),
                    authority                   = cleaned_data['authority'],
                    bank_acct_no                = cleaned_data['bank_acct_no'],
                    bank_acct_name              = cleaned_data['bank_acct_name'],

                    state                       = u'Taiwan',
                    country                     = u'ROC',
                    postal                      = '???',
                    city                        = service_region,
                    district                    = '???',
                    tag                         = [cleaned_data['npo_name'], service_region],
                    npo_rating                  = 0,
            )
            npoObjKey = npoObj.put()

            npoPhoneObj = NpoPhone(
                    npo_profile_ref         = npoObjKey,
                    phone_type              = "Fixed",
                    phone_no                = cleaned_data['telephone'],
            )
            npoPhoneObj.put()

            if cleaned_data['fax']:
                npoPhoneObj = NpoPhone(
                        npo_profile_ref         = npoObjKey,
                        phone_type              = "Fax",
                        phone_no                = cleaned_data['fax'],
                )
                npoPhoneObj.put()

            people = set()
            count = request.POST['adminAcctCount'] if request.POST['adminAcctCount'] <= 10 else 10
            for i in range(1, count + 1):
                if request.POST['adminaccount-'+i]:
                    people.add(request.POST['adminaccount-'+i])
            for person in people:
                person = flowBase.getVolunteer(person)
                if person:
                    personObj = NpoAdmin(
                            npo_profile_ref             = npoObjKey,
                            admin_role                  = 'Main',
                            volunteer_id                = person,
                    )
                    personObj.put()

            if cleaned_data['contact']:
                personObj = NpoContact(
                        npo_profile_ref                 = npoObjKey,
                        contact_type                    = 'Majoy',
                        contact_name                    = cleaned_data['contact'],
                        contact_email                   = user.email(),
                        volunteer_id                    = user,
                )
                personObj.put()

            return HttpResponseRedirect("/npo/?from=register&r=True")

    template_values = {
            'base':                     flowBase.getBase(request, user),
            'isWarning':                isWarning,
            'form':                     form,
    }
    return render_to_response('registration/npo_step3.html', template_values)
