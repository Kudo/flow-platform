from django.newforms import fields

class FlowChoiceField(fields.ChoiceField):
    def clean(self, value):
        value = super(fields.ChoiceField, self).clean(value)
        if value in fields.EMPTY_VALUES:
            value = u''
        value = fields.smart_unicode(value)
        if value == u'':
            return value
        valid_values = [k for k, v in self.choices]
        if value not in valid_values:
            raise fields.ValidationError(fields.gettext(u'Select a valid choice. That choice is not one of the available choices.'))
        return value