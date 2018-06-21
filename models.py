from peewee import *
from pyplanet.core.db import TimedModel
import json


class JsonField(TextField):
    def db_value(self, value):
        return json.dumps(value)

    def python_value(self, value):
        return json.loads(value)


class Manialink(TimedModel):
    name = CharField(
        max_length=255,
        null=False,
        help_text='Name of the manialink'
    )

    type = TextField(null=False, default=None, help_text='The type of the entry (text, image or xml)')

    show = BooleanField(null=False, default=True, help_text='Specifies if the manialink should be shown or not')

    data = JsonField(null=False)
