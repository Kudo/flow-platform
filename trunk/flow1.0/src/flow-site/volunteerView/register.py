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
from db import proflist
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

class MyCheckboxSelectMultiple(forms.widgets.CheckboxSelectMultiple):
    displayRowCount = 3
    def render(self, name, value, attrs=None, choices=()):
        from django.utils.html import escape
        if value is None: value = []
        has_id = attrs and attrs.has_key('id')
        final_attrs = self.build_attrs(attrs, name=name)
        output = [u'<table>\n<tr>']
        str_values = set([forms.util.smart_unicode(v) for v in value]) # Normalize to strings.
        for i, (option_value, option_label) in enumerate(chain(self.choices, choices)):
            # If an ID attribute was given, add a numeric index as a suffix,
            # so that the checkboxes don't all have the same ID attribute.
            if has_id:
                final_attrs = dict(final_attrs, id='%s_%s' % (attrs['id'], i))
            cb = forms.CheckboxInput(final_attrs, check_test=lambda value: value in str_values)
            option_value = forms.util.smart_unicode(option_value)
            rendered_cb = cb.render(name, option_value)
            output.append(u'<td>%s %s</td>' % (rendered_cb, escape(forms.util.smart_unicode(option_label))))
            if ((i + 1) % self.displayRowCount == 0):
                output.append(u'</tr>\n<tr>')
        output.append(u'</tr>\n</table>')
        return u'\n'.join(output)

"""
# -------------------------------------------------------------
# End Inject widgets
# -------------------------------------------------------------
"""

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
    alternate_email             = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'field text large', 'size': '50' }))

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
    expertise                   = forms.MultipleChoiceField(choices=choices, widget=MyCheckboxSelectMultiple())
    brief_intro                 = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'field textarea medium', 'cols': '50', 'rows': '10'}))

    class Meta:
        model = VolunteerProfile
        fields = ['volunteer_first_name', 'volunteer_last_name', 'sex', 'resident_city', 'logo', 'school', 'organization', 'title',
                  'alternate_email', 'cellphone_no', 'blog', 'expertise', 'brief_intro',
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


def step1(request):
    if 'register' in request.GET:
        return HttpResponseRedirect('/volunteer/register/step2/')
    template_values = {
            'base':                     flowBase.getBase(request),
    }
    return render_to_response('registration/volunteer_step1.html', template_values)

def step2(request):
    isWarning = None
    base = flowBase.getBase(request)
    if base['user']:
        return HttpResponseRedirect('/volunteer/register/step3/')
    if 'registered' in request.GET:
        isWarning = u'這個帳號已經註冊至若水平台，請試著以其他帳號註冊。'
    if 'logingaccount' in request.GET:
        return HttpResponseRedirect('/login?redirect=/volunteer/register/step3/')
    template_values = {
            'base':                     base,
            'isWarning':                isWarning,
    }
    return render_to_response('registration/volunteer_step2.html', template_values)

def step3(request):
    base = flowBase.getBase(request)
    if not base['user']:
        return HttpResponseRedirect('/volunteer/register/')
    if base['volunteer']:
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
                    volunteer_id                = base['user'], 
                    gmail                       = base['user'].email(),
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
                    cellphone_no                = cellphone_no,
                    blog                        = cleaned_data['blog'] or None,
                    expertise                   = cleaned_data['expertise'],
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
            'base':                     base,
            'isWarning':                isWarning,
            'form':                     form,
    }
    return render_to_response('registration/volunteer_step3.html', template_values)


