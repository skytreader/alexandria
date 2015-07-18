from wtforms import HiddenField
import json

class JsonField(HiddenField):
    """
    JsonField is a subclass of HiddenField since you won't really make your users
    input JSON data directly no? Most likely, the use case is that the value of
    this field is automagically generated from other fields.
    """

    def pre_validate(self, form):
        superv = super(JsonField, self).pre_validate(form)
        jsonv = True

        try:
            json.loads(self.raw_data[0])
        except ValueError, TypeError:
            jsonv = False

        return superv and jsonv
