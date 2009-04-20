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
from db.ddl import NpoProfile, NpoContact, NpoPhone, NpoEmail, NpoNews, NpoAdmin
from itertools import chain
from django.conf import settings
from google.appengine.ext.webapp import template
try:
    from django import newforms as forms
except ImportError:
    from django import forms
from google.appengine.ext.db import djangoforms
from common.fields import FlowChoiceField

maxAdminCount = 10

def _makeFields(fieldDataFormat, endNum, startNum=1):
    for i in range(startNum, endNum + 1):
        yield fieldDataFormat % (i)

class NpoProfileForm(djangoforms.ModelForm):
    npo_name                    = forms.CharField(max_length=15, widget=forms.TextInput(attrs={'class': 'field text medium'}))
    founder                     = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'class': 'field text medium'}))
    brief_intro                 = forms.CharField(widget=forms.Textarea(attrs={'class': 'field textarea medium', 'cols': '50', 'rows': '10'}))
    logo                        = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'field text large'}))

    choices = [(region, region) for region in flowBase.getRegion()]
    service_region              = FlowChoiceField(choices=choices, widget=forms.Select(attrs={'class': 'field select'}))

    service_target              = forms.CharField(widget=forms.TextInput(attrs={'class': 'field text medium'}))
    service_field               = forms.CharField(widget=forms.TextInput(attrs={'class': 'field text medium'}))
    contact                     = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'class': 'field text medium'}))
    website                     = forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={'class': 'field text', 'size': '50'}))
    blog                        = forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={'class': 'field text', 'size': '50'}))
    telephone                   = forms.CharField(max_length=20,  widget=forms.TextInput(attrs={'class': 'field text medium'}))
    fax                         = forms.CharField(max_length=20,  required=False, widget=forms.TextInput(attrs={'class': 'field text medium'}))

    foundyear                   = forms.CharField(min_length=4, max_length=4, widget=forms.TextInput(attrs={'class': 'field text', 'size': '4'}))
    foundmonth                  = forms.CharField(min_length=1, max_length=2, widget=forms.TextInput(attrs={'class': 'field text', 'size': '2'}))
    foundday                    = forms.CharField(min_length=1, max_length=2, widget=forms.TextInput(attrs={'class': 'field text', 'size': '2'}))

    authority                   = forms.CharField(required=False, initial='無', widget=forms.TextInput(attrs={'class': 'field text medium'}))
    bank_acct_no                = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'field text medium'}))
    bank_acct_name              = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'field text medium'}))

    adminAcctCount              = forms.CharField(required=False, initial=1, widget=forms.HiddenInput())
    adminaccount_1              = forms.CharField(required=False, max_length=255, widget=forms.TextInput(attrs={'class': 'field text', 'size': '50'}))
    for cmd in _makeFields("adminaccount_%d = forms.CharField(required=False, max_length=255, widget=forms.TextInput(attrs={'style': 'display: none;', 'class': 'field text', 'size': '50'}))", maxAdminCount, startNum=2):
        exec(cmd)

    def clean_npo_name(self):
        self.cleaned_data = self._cleaned_data()
        data = self.cleaned_data['npo_name']
        if db.GqlQuery('SELECT * FROM NpoProfile WHERE npo_name = :1', data).count() > 0:
            raise forms.ValidationError(u'這個公益團體名稱已經被註冊了，請試著以其他名稱註冊。')
        return data

    class Meta:
        model = NpoProfile
        fields = ['npo_name', 'founder', 'brief_intro', 'logo',
                  'service_region', 'service_target', 'service_field',
                  'website', 'blog', 'authority', 'bank_acct_no', 'bank_acct_name',
                 ]

def step1(request):
    isWarning = None
    user = users.get_current_user()
    if (not flowBase.getVolunteer(user)) or ('notMember' in request.GET):
        isWarning = u'您尚未註冊至若水平台，請先點選右上角註冊後才能申請註冊公益團體喔。'
    if NpoProfile.all().filter('google_acct = ', user).count() > 10:
        isWarning = u'本系統限制一個人最多只能申請十個公益團體，如有問題，請洽管理者。'
    if 'yes' in request.GET:
        return HttpResponseRedirect('/npo/register/step2/')
    if 'no' in request.GET:
        return HttpResponseRedirect('/')
    template_values = {
            'base':                     flowBase.getBase(request),
            'isWarning':                isWarning
    }
    return render_to_response('registration/npo_step1.html', template_values)

def step2(request):
    user = users.get_current_user()
    if not flowBase.getVolunteer(user):
        return HttpResponseRedirect('/npo/register/?notMember=True')
    if NpoProfile.all().filter('google_acct = ', user).count() > 10:
        return HttpResponseRedirect('/npo/register/')
    if 'register' in request.GET:
        return HttpResponseRedirect('/npo/register/step3/')
    template_values = {
            'base':                     flowBase.getBase(request),
    }
    return render_to_response('registration/npo_step2.html', template_values)

def step3(request):
    isWarning = None
    user = flowBase.getVolunteer(users.get_current_user())
    if not user:
        return HttpResponseRedirect('/npo/register/?notMember=True')
    if NpoProfile.all().filter('google_acct = ', users.get_current_user()).count() > 10:
        return HttpResponseRedirect('/npo/register/')

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
            npoObj = NpoProfile(
                    google_acct                 = user.volunteer_id,
                    create_time                 = now,
                    update_time                 = now,
                    status                      = "normal",
                    valid_google_acct           = True,

                    npo_name                    = cleaned_data['npo_name'],
                    founder                     = cleaned_data['founder'],
                    brief_intro                 = cleaned_data['brief_intro'],
                    logo                        = cleaned_data['logo'] or None,
                    service_region              = [cleaned_data['service_region']],
                    service_target              = [cleaned_data['service_target']],
                    service_field               = [cleaned_data['service_field']],
                    website                     = cleaned_data['website'] or None,
                    blog                        = cleaned_data['blog'] or None,
                    founding_date               = datetime.date(int(cleaned_data['foundyear']), int(cleaned_data['foundmonth']), int(cleaned_data['foundday'])),
                    authority                   = cleaned_data['authority'],
                    bank_acct_no                = cleaned_data['bank_acct_no'],
                    bank_acct_name              = cleaned_data['bank_acct_name'],

                    state                       = u'Taiwan',
                    country                     = u'ROC',
                    postal                      = '???',
                    city                        = cleaned_data['service_region'],
                    district                    = '???',
                    tag                         = [cleaned_data['npo_name'], cleaned_data['service_region']],
                    npo_rating                  = 0,
                    docs_link                   = ['???'],
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

            flowBase.addVolunteer2Npo(user, npoObj)
            flowBase.addVolunteer2NpoAdmin(user, npoObj)

            people = set()
            count = cleaned_data['adminAcctCount'] if cleaned_data['adminAcctCount'] <= maxAdminCount else maxAdminCount
            for i in range(1, count + 1):
                i = str(i)
                if cleaned_data['adminaccount_'+i]:
                    people.add(cleaned_data['adminaccount_'+i])
            for person in people:
                person = flowBase.getVolunteer(person)
                flowBase.addVolunteer2Npo(person, npoObj)
                flowBase.addVolunteer2NpoAdmin(person, npoObj)

            if cleaned_data['contact']:
                personObj = NpoContact(
                        npo_profile_ref                 = npoObjKey,
                        contact_type                    = 'Major',
                        contact_name                    = cleaned_data['contact'],
                        contact_email                   = user.volunteer_id.email(),
                        volunteer_id                    = user.volunteer_id,
                )
                personObj.put()

            return HttpResponseRedirect("/npo/?from=register&r=True")

    template_values = {
            'base':                     flowBase.getBase(request),
            'myRealName':               u', '.join([user.volunteer_last_name, user.volunteer_first_name]),
            'isWarning':                isWarning,
            'form':                     form,
            'formAdminList':            [eval('form["adminaccount_%d"]' % (i)) for i in range(2, maxAdminCount + 1)],
            'maxAdminCount':            maxAdminCount,
    }
    return render_to_response('registration/npo_step3.html', template_values)
