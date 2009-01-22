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
from db.ddl import VolunteerProfile, VolunteerIm, CountryCity
from itertools import chain
from django.conf import settings
from google.appengine.ext.webapp import template
try:
    from django import newforms as forms
except ImportError:
    from django import forms
from google.appengine.ext.db import djangoforms

"""
# -------------------------------------------------------------
# Inject to RadioSelect
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
# End Inject to RadioSelect
# -------------------------------------------------------------
"""

def step1(request):
    if 'register' in request.GET:
        return HttpResponseRedirect('/volunteer/register/step2/')
    template_values = {
            'base':                     flowBase.getBase(request),
    }
    return render_to_response('registration/volunteer_step1.html', template_values)

def step2(request):
    isWarning = None
    if users.get_current_user():
        return HttpResponseRedirect('/volunteer/register/step3/')
    if 'registered' in request.GET:
        isWarning = u'這個帳號已經註冊至若水平台，請試著以其他帳號註冊。'
    if 'logingaccount' in request.GET:
        return HttpResponseRedirect('/login?redirect=/volunteer/register/step3/')
    template_values = {
            'base':                     flowBase.getBase(request),
            'isWarning':                isWarning,
    }
    return render_to_response('registration/volunteer_step2.html', template_values)

def step3(request):
    user = users.get_current_user()
    if not user:
        return HttpResponseRedirect('/volunteer/register/')
    if db.GqlQuery('SELECT * FROM VolunteerProfile WHERE volunteer_id = :1', user).count() > 0:
        return HttpResponseRedirect('/logout?redirect=/volunteer/register/step2/?registered=True')
    isWarning = None
    if request.method != 'POST':
        form = VolunteerProfileForm()
    else:
        form = VolunteerProfileForm(data=request.POST)
        if not form.is_valid():
            isWarning = u'請檢查是否有資料輸入錯誤。'
        else:
            import datetime
            now = datetime.datetime.utcnow()
            cleaned_data = form._cleaned_data()
            if cleaned_data['phone1'] and cleaned_data['phone2'] and cleaned_data['phone3']:
                cellphone_no = '%s-%s-%s' % (cleaned_data['phone1'], cleaned_data['phone2'], cleaned_data['phone3'])
            else:
                cellphone_no = None
            resident_city = db.GqlQuery('SELECT * From CountryCity WHERE city_en = :1', cleaned_data['resident_city']).get().city_tc
            volunteerObj = VolunteerProfile(
                    volunteer_id                = user, 
                    gmail                       = user.email(),
                    create_time                 = now,
                    update_time                 = now,
                    status                      = "normal",
                    valid_google_acct           = True,

                    volunteer_first_name        = cleaned_data['volunteer_first_name'], 
                    volunteer_last_name         = cleaned_data['volunteer_last_name'], 
                    sex                         = cleaned_data['sex'],
                    date_birth                  = datetime.date(int(cleaned_data['birthyear']), int(cleaned_data['birthmonth']), int(cleaned_data['birthday'])),
                    resident_city               = resident_city,
                    logo                        = cleaned_data['logo'] or None,
                    school                      = cleaned_data['school'],
                    organization                = cleaned_data['organization'],
                    title                       = cleaned_data['title'],
                    hide_cellphone              = cleaned_data['hide_cellphone'],
                    cellphone_no                = cellphone_no,
                    hide_blog                   = cleaned_data['hide_blog'],
                    blog                        = cleaned_data['blog'] or None,
                    expertise                   = [cleaned_data['expertise']],
                    concern                     = cleaned_data['concern'],
                    message                     = cleaned_data['message'],
                    brief_intro                 = cleaned_data['brief_intro'],

                    id_no                       = '???',
                    resident_state              = u'Taiwan',
                    resident_country            = u'ROC',
                    resident_postal             = '???',
                    resident_district           = '???',
                    prefer_region               = [cleaned_data['resident_city']],
                    prefer_zip                  = ['???'],
                    prefer_target               = ['???'],
                    prefer_field                = ['???'],
                    prefer_group                = ['???'],
                    volunteer_rating            = 0,
                    phone_no                    = cellphone_no or '0000-0000',
            )
            volunteerObjKey = volunteerObj.put()

            imTypeTable = {
                    'MSN':                      'http://messenger.msn.com/',
                    'Yahoo Messenger':          'http://messenger.yahoo.com/',
            }

            if cleaned_data['im_account']:
                volunteerIMObj = VolunteerIm(
                        volunteer_profile_ref       = volunteerObjKey,
                        im_type                     = cleaned_data['im_type'],
                        im_account                  = '%s %s' % (imTypeTable[cleaned_data['im_type']], cleaned_data['im_account'])
                )
                volunteerIMObj.put()

            return HttpResponseRedirect("/?from=register&r=True")

    template_values = {
            'base':                     flowBase.getBase(request),
            'isWarning':                isWarning,
            'form':                     form,
    }
    return render_to_response('registration/volunteer_step3.html', template_values)

class VolunteerProfileForm(djangoforms.ModelForm):
    volunteer_first_name        = forms.CharField(widget=forms.TextInput(attrs={'class': 'field text'}))
    volunteer_last_name         = forms.CharField(widget=forms.TextInput(attrs={'class': 'field text'}))
    sex                         = forms.ChoiceField(choices=(('Male', u'男性'), ('Female', u'女性')), widget=MyRadioSelect(attrs={'class': 'field radio'}))

    birthyear                   = forms.CharField(min_length=4, max_length=4, widget=forms.TextInput(attrs={'class': 'field text', 'size': '4'}))
    birthmonth                  = forms.CharField(min_length=1, max_length=2, widget=forms.TextInput(attrs={'class': 'field text', 'size': '2'}))
    birthday                    = forms.CharField(min_length=1, max_length=2, widget=forms.TextInput(attrs={'class': 'field text', 'size': '2'}))

    choices = []
    citys = db.GqlQuery('SELECT * FROM CountryCity WHERE state_en = :1', 'Taiwan').fetch(50)
    for city in citys:
        choices.append((city.city_en, city.city_tc))
    del citys
    resident_city               = forms.ChoiceField(choices=choices, widget=forms.Select(attrs={'class': 'field select'}))

    logo                        = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'field text large'}))
    school                      = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'field text medium'}))
    organization                = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'field text medium'}))
    title                       = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'field text medium'}))
    hide_email                  = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'field checkbox'}))
    alternate_email             = forms.CharField(widget=forms.TextInput(attrs={'class': 'field text large', 'maxlength': '255', 'size': '50' }))

    hide_im                     = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'field checkbox'}))
    choices = (
            ('MSN',                     u'MSN 即時通訊'),
            ('Yahoo Messenger',         u'Yahoo! 即時通訊'),
    )
    im_type                     = forms.ChoiceField(required=False, choices=choices, widget=forms.Select(attrs={'class': 'field select'}))
    im_account                  = forms.CharField(required=False, max_length=255, widget=forms.TextInput(attrs={'class': 'field text large', 'size': '30'}))

    hide_cellphone              = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'field checkbox', 'checked': 'checked'}))
    phone1                      = forms.CharField(required=False, min_length=4, max_length=4, widget=forms.TextInput(attrs={'class': 'field text', 'size': '4'}))
    phone2                      = forms.CharField(required=False, min_length=3, max_length=3, widget=forms.TextInput(attrs={'class': 'field text', 'size': '3'}))
    phone3                      = forms.CharField(required=False, min_length=3, max_length=3, widget=forms.TextInput(attrs={'class': 'field text', 'size': '3'}))

    hide_blog                   = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'field checkbox'}))
    blog                        = forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={'class': 'field text', 'size': '50'}))
    expertise                   = forms.CharField(widget=forms.TextInput(attrs={'class': 'field text medium'}))
    concern                     = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'field textarea medium', 'cols': '50', 'rows': '10'}))
    message                     = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'field textarea medium', 'cols': '50', 'rows': '10'}))
    brief_intro                 = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'field textarea medium', 'cols': '50', 'rows': '10'}))

    class Meta:
        model = VolunteerProfile
        fields = ['volunteer_first_name', 'volunteer_last_name', 'sex', 'resident_city', 'logo', 'school', 'organization', 'title',
                  'hide_email', 'alternate_email', 'hide_im', 'hide_cellphone', 'cellphone_no', 'hide_blog', 'blog',
                  'expertise', 'concern', 'message', 'brief_intro',
                 ]

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
    return render_to_response('volunteer/profile_info.html', template_values)

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
                'sex':                      user.sex,
                'email':                    user.gmail,
                'im':                       '%s：%s' % ( userIM.im_type, userIM.im_account.address) if userIM else '無',
                'cellphone_no':             user.cellphone_no,
                'blog':                     user.blog,
                'brief_intro':              user.brief_intro or '無',
                'form':                     VolunteerProfileForm(data=request.POST, instance=user),
        }
        return render_to_response('volunteer/profile_edit.html', template_values)
