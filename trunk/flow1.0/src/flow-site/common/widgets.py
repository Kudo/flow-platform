# -*- coding: big5 -*-
import datetime
from itertools import chain
from django import newforms as forms

class TimeInput(forms.TextInput):
    def render(self, name, value, attrs=None):
        if isinstance(value,datetime.time):
            value=value.strftime('%H:%M')
        return ('&nbsp;'*3)+super(TimeInput,self).render(name, value, attrs)
        
class FlowSplitDateTimeWidget(forms.SplitDateTimeWidget):
    def __init__(self, attrs=None):
        dicDateAttrs={'class':'datePicker','size':10,'value':u'請輸入日期'}
        dicTimeAttrs={'class':'timePicker','size':5,'value':u'請輸入時間'}
        if attrs:
            dicDateAttrs.update(attrs)
            dicTimeAttrs.update(attrs)
        widgets = (forms.TextInput(attrs=dicDateAttrs), TimeInput(attrs=dicTimeAttrs))
        super(forms.SplitDateTimeWidget, self).__init__(widgets, attrs)

class FlowCheckboxSelectMultiple(forms.widgets.CheckboxSelectMultiple):
    displayRowCount = 4
    def render(self, name, value, attrs=None, choices=()):
        from django.utils.html import escape
        if value is None: value = []
        has_id = attrs and attrs.has_key('id')
        final_attrs = self.build_attrs(attrs, name=name)
        output = [u'<table>\n<tr>']
        if isinstance(value, list):
            str_values = set([forms.util.smart_unicode(v) for v in value]) # Normalize to strings.
        else:
            str_values = set([forms.util.smart_unicode(v) for v in value.split('\n')]) # Normalize to strings.
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

class FlowExpertiseChoiceWidget(forms.widgets.CheckboxSelectMultiple):
    displayRowCount = 4
    def render(self, name, value, attrs=None, choices=()):
        from db import proflist
        output = [u' ']
        if value is None: value = []
        i = 0
        output.append(u'<div class="section">專業領域</div>')
        output.append(u'<div class="block clearfix">')
        for prof in proflist.profList:
            output.append(u'<span class="checkbox">')
            if prof in value:
                output.append(u'<input class="field checkbox" id="id_expertise_%d" type="checkbox" value="%s" name="%s" checked/>' % (i, prof,name))
            else:
                output.append(u'<input class="field checkbox" id="id_expertise_%d" type="checkbox" value="%s" name="%s"/>' % (i, prof,name))
            output.append(u'<label class="choice" for="id_expertise_%d">%s</label>' % (i, prof))
            output.append(u'</span>')
            if ((i + 1) % self.displayRowCount == 0):
                output.append(u'</div><div class="block clearfix">')
            i += 1
        output.append(u'</div>')
        
        output.append(u'<div class="section">語言專長</div>')
        output.append(u'<div class="block clearfix">')
        for prof in proflist.langList:
            output.append(u'<span class="checkbox">')
            if prof in value:
                output.append(u'<input class="field checkbox" id="id_expertise_%d" type="checkbox" value="%s" name="%s" checked/>' % (i, prof,name))
            else:
                output.append(u'<input class="field checkbox" id="id_expertise_%d" type="checkbox" value="%s" name="%s"/>' % (i, prof,name))
            output.append(u'<label class="choice" for="id_expertise_%d">%s</label>' % (i, prof))
            output.append(u'</span>')
            if ((i + 1) % self.displayRowCount == 0):
                output.append(u'</div><div class="block clearfix">')
            i += 1
        output.append(u'</div>')
        
        '''
        output.append(u'<tr><td><h3>%s</h3></td></tr>' % (u'專業領域'))
        output.append(u'<tr>')
        for value in proflist.profList:
            output.append(u'<td><input id="id_expertise_%d" type="checkbox" value="%s" name="expertise"/>%s</td>' % (i, value, value))
            if ((i + 1) % self.displayRowCount == 0):
                output.append(u'</tr>\n<tr>')
            i += 1
        output.append(u'</tr>')

        output.append(u'<tr><td><h3>%s</h3></td></tr>\n' % (u'語言專長'))
        output.append(u'<tr>')
        for value in proflist.langList:
            output.append(u'<td><input id="id_expertise_%d" type="checkbox" value="%s" name="expertise"/>%s</td>' % (i, value, value))
            if ((i + 1) % self.displayRowCount == 0):
                output.append(u'</tr>\n<tr>')
            i += 1

        output.append(u'</tr>\n</table>')
        '''
        
        return u'\n'.join(output)        
