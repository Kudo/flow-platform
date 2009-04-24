from django.newforms import fields
from google.appengine.ext import db

class FlowChoiceField(fields.ChoiceField):
    def clean(self, value):
        value = super(fields.ChoiceField, self).clean(value)
        if value in fields.EMPTY_VALUES:
            value = u''
        value = fields.smart_unicode(value)
        if value == u'':
            return value
        valid_values = set([k for k, v in self.choices])
        if value not in valid_values:
            raise fields.ValidationError(fields.gettext(u'Select a valid choice. That choice is not one of the available choices.'))
        return value

class ListURLField(fields.URLField):
    def clean(self, value):
        value=super(ListURLField,self).clean(value)
        if value:
            value=[db.Link(value)]
        else:
            value=[]
        return value
