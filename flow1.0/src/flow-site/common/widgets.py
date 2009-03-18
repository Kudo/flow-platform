# -*- coding: big5 -*-
import datetime
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