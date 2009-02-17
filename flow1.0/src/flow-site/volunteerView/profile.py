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

"""
# -------------------------------------------------------------
# Inject to some widgets
# for custom layout and a bug fix in django 0.9.6
# -------------------------------------------------------------
"""
class MyRadioInput(forms.widgets.RadioInput):
    def __unicode__(self):
        return u'%s\n<label for="%s">%s</label>' % (self.tag(), self.choice_value, self.choice_label)

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
    sex                         = forms.ChoiceField(choices=(('Male', u'男性'), ('Female', u'女性')), widget=MyRadioSelect())

    birthyear                   = forms.CharField(min_length=4, max_length=4, widget=forms.TextInput(attrs={'size': '4'}))
    birthmonth                  = forms.CharField(min_length=1, max_length=2, widget=forms.TextInput(attrs={'size': '2'}))
    birthday                    = forms.CharField(min_length=1, max_length=2, widget=forms.TextInput(attrs={'size': '2'}))

    choices = []
    citys = db.GqlQuery('SELECT * FROM CountryCity WHERE state_en = :1', 'Taiwan').fetch(50)
    for city in citys:
        choices.append((city.city_en, city.city_tc))
    del citys
    resident_city               = forms.ChoiceField(choices=choices)

    choices = (
            ('MSN',                     u'MSN 即時通訊'),
            ('Yahoo Messenger',         u'Yahoo! 即時通訊'),
    )
    im_type                     = forms.ChoiceField(required=False, choices=choices)
    im_account                  = forms.CharField(required=False, max_length=255, widget=forms.TextInput(attrs={'size': '30'}))

    phone1                      = forms.CharField(required=False, min_length=4, max_length=4, widget=forms.TextInput(attrs={'class': 'field text', 'size': '4'}))
    phone2                      = forms.CharField(required=False, min_length=3, max_length=3, widget=forms.TextInput(attrs={'class': 'field text', 'size': '3'}))
    phone3                      = forms.CharField(required=False, min_length=3, max_length=3, widget=forms.TextInput(attrs={'class': 'field text', 'size': '3'}))

    blog                        = forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={'size': '50'}))

    choices = [(entry.encode('UTF-8'), entry) for entry in proflist.getProfessionList()]
    expertise                   = forms.MultipleChoiceField(choices=choices, widget=MyCheckboxSelectMultiple())
    brief_intro                 = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'field textarea medium', 'cols': '50', 'rows': '5'}))

    class Meta:
        model = VolunteerProfile
        fields = ['volunteer_first_name', 'volunteer_last_name', 'sex', 'resident_city', 'logo', 'school', 'organization', 'title',
                  'cellphone_no', 'blog', 'expertise', 'brief_intro',
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
        return HttpResponseRedirect('/')
    userIM = user.im2volunteer.get()
    template_values = {
            'isSelf':                   isSelf,
            'base':                     flowBase.getBase(request, volunteer=user),
            'sex':                      user.sex,
            'cellphone_no':             (user.cellphone_no or u'無'),
            'blog':                     user.blog,
            'email':                    re.sub('(.+)@(.+)', '\\1 (at) \\2', user.gmail),
            'im':                       u'%s：%s' % ( userIM.im_type, userIM.im_account.address) if userIM else u'無',
            'school':                   user.school or u'無',
            'organization':             user.organization or u'無',
            'title':                    user.title or u'無',
            'expertise':                u', '.join(user.expertise),
            'brief_intro':              user.brief_intro or u'無',
    }
    response = render_to_response('volunteer/profile_info.html', template_values)

    return response


def edit(request):
    if not users.get_current_user():
        return HttpResponseRedirect('/')

    user = db.GqlQuery('SELECT * FROM VolunteerProfile WHERE volunteer_id = :1', users.get_current_user()).get()
    if not user:
        return HttpResponseRedirect('/')

    userIM = user.im2volunteer.get()
    isWarning = None
    if request.method != 'POST':
        [phone1, phone2, phone3] = user.cellphone_no.split('-')
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
            return HttpResponseRedirect('/volunteer/profile/')
        form = VolunteerProfileForm(data=request.POST)
        if not form.is_valid():
            isWarning = u'請檢查是否有資料輸入錯誤。'
        else:
            cleaned_data = form._cleaned_data()
            if cleaned_data['phone1'] and cleaned_data['phone2'] and cleaned_data['phone3']:
                cellphone_no = '%s-%s-%s' % (cleaned_data['phone1'], cleaned_data['phone2'], cleaned_data['phone3'])
            else:
                cellphone_no = None
            resident_city = db.GqlQuery('SELECT * From CountryCity WHERE city_en = :1', cleaned_data['resident_city']).get().city_tc

            user.update_time                 = datetime.datetime.utcnow()
            user.volunteer_first_name        = cleaned_data['volunteer_first_name']
            user.volunteer_last_name         = cleaned_data['volunteer_last_name']
            user.sex                         = cleaned_data['sex']
            user.date_birth                  = datetime.date(int(cleaned_data['birthyear']), int(cleaned_data['birthmonth']), int(cleaned_data['birthday']))
            user.resident_city               = resident_city
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
                volunteerIMObj = VolunteerIm(
                        volunteer_profile_ref       = volunteerObjKey,
                        im_type                     = cleaned_data['im_type'],
                        im_account                  = '%s %s' % (imTypeTable[cleaned_data['im_type']], cleaned_data['im_account'])
                )
                volunteerIMObj.put()

            return HttpResponseRedirect("/volunteer/profile/")

    template_values = {
            'base':                     flowBase.getBase(request, volunteer=user),
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
