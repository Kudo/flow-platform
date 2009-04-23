#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import cgi
import datetime
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from google.appengine.ext import db
from google.appengine.api import users
import flowBase
from db import proflist
from db.ddl import VolunteerProfile, VolunteerIm
from itertools import chain
from django.conf import settings
from google.appengine.ext.webapp import template
try:
    from django import newforms as forms
except ImportError:
    from django import forms
from google.appengine.ext.db import djangoforms
from common.fields import FlowChoiceField
from common.widgets import FlowExpertiseChoiceWidget

"""
# -------------------------------------------------------------
# Inject to some widgets
# for custom layout and a bug fix in django 0.9.6
# -------------------------------------------------------------
"""
class MyRadioInput(forms.widgets.RadioInput):
    def __unicode__(self):
        return u'%s\n<label class="choice" for="%s">%s</label>' % (self.tag(), self.choice_value, self.choice_label)

class MyRadioFieldRenderer(forms.widgets.RadioFieldRenderer):
    def __unicode__(self):
        "Outputs my custom view for radio fields."
        return u'\n'.join([u'%s' % w for w in self])
    __str__ = __unicode__

    def __iter__(self):
        for i, choice in enumerate(self.choices):
            yield MyRadioInput(self.name, self.value, self.attrs.copy(), choice, i)

class MyRadioSelect(forms.widgets.Select):
    def render(self, name, value, attrs=None, choices=()):
        "Returns a MyRadioFieldRenderer instance rather than a Unicode string."
        if value is None: value = ''
        str_value = forms.util.smart_unicode(value) # Normalize to string.
        attrs = self.attrs or {}
        return MyRadioFieldRenderer(name, str_value, attrs, list(chain(self.choices, choices)))

"""
# -------------------------------------------------------------
# End Inject widgets
# -------------------------------------------------------------
"""

class VolunteerProfileForm(djangoforms.ModelForm):
    volunteer_first_name        = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'class': 'field text'}))
    volunteer_last_name         = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'class': 'field text'}))
    nickname                    = forms.CharField(max_length=25, widget=forms.TextInput(attrs={'class': 'field text'}))

    sex                         = forms.ChoiceField(choices=(('Male', u'男性'), ('Female', u'女性')), widget=MyRadioSelect(attrs={'class': 'field radio'}))

    birthyear                   = forms.CharField(min_length=4, max_length=4, widget=forms.TextInput(attrs={'class': 'field text', 'size': '4'}))
    birthmonth                  = forms.CharField(min_length=1, max_length=2, widget=forms.TextInput(attrs={'class': 'field text', 'size': '2'}))
    birthday                    = forms.CharField(min_length=1, max_length=2, widget=forms.TextInput(attrs={'class': 'field text', 'size': '2'}))

    choices = [(region, region) for region in flowBase.getResident()]
    resident_city               = FlowChoiceField(choices=choices, widget=forms.Select(attrs={'class': 'field select'}))

    logo                        = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'field text large'}))
    school                      = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'field text medium'}))
    organization                = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'field text medium'}))
    title                       = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'field text medium'}))


    choices = (
            ('MSN',                     u'MSN 即時通訊'),
            ('Yahoo Messenger',         u'Yahoo! 即時通訊'),
    )
    im_type                     = forms.ChoiceField(required=False, choices=choices, widget=forms.Select(attrs={'class': 'field select'}))
    im_account                  = forms.CharField(required=False, max_length=255, widget=forms.TextInput(attrs={'class': 'field text large', 'size': '30'}))

    phone1                      = forms.CharField(required=False, min_length=4, max_length=4, widget=forms.TextInput(attrs={'class': 'field text', 'size': '4'}))
    phone2                      = forms.CharField(required=False, min_length=3, max_length=3, widget=forms.TextInput(attrs={'class': 'field text', 'size': '3'}))
    phone3                      = forms.CharField(required=False, min_length=3, max_length=3, widget=forms.TextInput(attrs={'class': 'field text', 'size': '3'}))

    blog                        = forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={'class': 'field text', 'size': '50'}))

    choices = [(entry.encode('UTF-8'), entry) for entry in proflist.getProfessionList()]
    expertise                   = forms.MultipleChoiceField(choices=choices, widget=FlowExpertiseChoiceWidget())
    brief_intro                 = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'field textarea medium', 'cols': '50', 'rows': '5'}))

    class Meta:
        model = VolunteerProfile
        fields = ['volunteer_first_name', 'volunteer_last_name', 'nickname', 'sex', 'resident_city', 'logo', 'school', 'organization', 'title',
                  'cellphone_no', 'blog', 'expertise', 'brief_intro',
                 ]

    def clean_birthyear(self):
        self.cleaned_data = self._cleaned_data()
        data = int(self.cleaned_data['birthyear'])
        if data < 1900 or data > 2030:
            raise forms.ValidationError(u'輸入的值不洽當，請試著輸入正確的值。')
        return data

    def clean_birthmonth(self):
        self.cleaned_data = self._cleaned_data()
        data = int(self.cleaned_data['birthmonth'])
        if data < 1 or data > 12:
            raise forms.ValidationError(u'輸入的值不洽當，請試著輸入正確的值。')
        return data

    def clean_birthday(self):
        self.cleaned_data = self._cleaned_data()
        data = int(self.cleaned_data['birthday'])
        if data < 1 or data > 31:
            raise forms.ValidationError(u'輸入的值不洽當，請試著輸入正確的值。')
        return data


def show(request, key):
    user = flowBase.verifyVolunteer(request, key)
    if not user:
        return HttpResponseRedirect('/')

    base = flowBase.getBase(request, 'volunteer')
    template_values = {
            'isSelf':                   True if base['user'] == user.volunteer_id else False,
            'base':                     base,
            'volunteerBase':            flowBase.getVolunteerBase(user),
            'page':                     'profile',
            'expertise':                u', '.join(user.expertise),
            'brief_intro':              user.brief_intro or u'無',
    }
    response = render_to_response('volunteer/profile_info.html', template_values)

    return response


def edit(request):
    base = flowBase.getBase(request, 'volunteer')
    user = flowBase.getVolunteer(base['user'])
    if not user:
        return HttpResponseRedirect('/')

    userIM = user.im2volunteer.get()
    isWarning = None
    if request.method != 'POST':
        try:
            (phone1, phone2, phone3) = user.cellphone_no.split('-')
        except:
            (phone1, phone2, phone3) = ('', '', '')
        customData = {
                'birthyear':        user.date_birth.year,
                'birthmonth':       user.date_birth.month,
                'birthday':         user.date_birth.day,
                'phone1':           phone1,
                'phone2':           phone2,
                'phone3':           phone3,
        }
        if userIM:
            customData['im_type'] = userIM.im_type
            customData['im_account'] = userIM.im_account.address

        form = VolunteerProfileForm(instance=user, initial=customData)
    else:
        if not request.POST['submit']:
            return HttpResponseRedirect('/volunteer/home/')
        form = VolunteerProfileForm(data=request.POST)
        if not form.is_valid():
            isWarning = u'請檢查是否有資料輸入錯誤。'
        else:
            cleaned_data = form._cleaned_data()
            if cleaned_data['phone1'] and cleaned_data['phone2'] and cleaned_data['phone3']:
                cellphone_no = '%s-%s-%s' % (cleaned_data['phone1'], cleaned_data['phone2'], cleaned_data['phone3'])
            else:
                cellphone_no = None

            user.update_time                 = datetime.datetime.utcnow()
            user.volunteer_first_name        = cleaned_data['volunteer_first_name']
            user.volunteer_last_name         = cleaned_data['volunteer_last_name']
            user.nickname                    = cleaned_data['nickname']
            user.sex                         = cleaned_data['sex']
            user.date_birth                  = datetime.date(int(cleaned_data['birthyear']), int(cleaned_data['birthmonth']), int(cleaned_data['birthday']))
            user.resident_city               = cleaned_data['resident_city']
            user.logo                        = cleaned_data['logo'] or None
            user.school                      = cleaned_data['school']
            user.organization                = cleaned_data['organization']
            user.title                       = cleaned_data['title']
            user.cellphone_no                = cellphone_no
            user.blog                        = cleaned_data['blog'] or None
            user.expertise                   = cleaned_data['expertise']
            user.brief_intro                 = cleaned_data['brief_intro']

            volunteerObjKey = user.put()

            imTypeTable = {
                    'MSN':                      'http://messenger.msn.com/',
                    'Yahoo Messenger':          'http://messenger.yahoo.com/',
            }

            if cleaned_data['im_account']:
                volunteerIMObj = VolunteerIm.all().filter('volunteer_profile_ref =', volunteerObjKey).get()
                if volunteerIMObj:
                    volunteerIMObj.im_type = cleaned_data['im_type']
                    volunteerIMObj.im_account = '%s %s' % (imTypeTable[cleaned_data['im_type']], cleaned_data['im_account'])
                else:
                    volunteerIMObj = VolunteerIm(
                            volunteer_profile_ref       = volunteerObjKey,
                            im_type                     = cleaned_data['im_type'],
                            im_account                  = '%s %s' % (imTypeTable[cleaned_data['im_type']], cleaned_data['im_account'])
                    )
                volunteerIMObj.put()

            return HttpResponseRedirect("/volunteer/home/")

    template_values = {
            'isSelf':                   True if base['user'] == user.volunteer_id else False,
            'base':                     base,
            'page':                     'home',
            'volunteerBase':            flowBase.getVolunteerBase(user),
            'isWarning':                isWarning,
            'form':                     form,
            'sex':                      user.sex,
            'email':                    user.gmail,
            'im':                       u'%s：%s' % ( userIM.im_type, userIM.im_account.address) if userIM else u'無',
            'cellphone_no':             user.cellphone_no,
            'blog':                     user.blog,
            'brief_intro':              user.brief_intro or u'無',
    }
    response = render_to_response('volunteer/profile_edit.html', template_values)
    return response
