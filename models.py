from peewee import *
from pyplanet.core.db import TimedModel
import json
from collections import defaultdict
import traceback


class JsonField(TextField):
    def db_value(self, value):
        return json.dumps(value)

    def python_value(self, value):
        return json.loads(value)


class Message(TimedModel):
    _typemap = defaultdict(lambda: -1, {'Text': 0, 'Image': 1, 'XML': 2, 'Chat': 3})
    _typemap2 = defaultdict(lambda: '', {0: 'Text', 1: 'Image', 2: 'XML', 3: 'Chat'})

    @classmethod
    def get_type_id(cls, typename):
        return cls._typemap[typename]

    @classmethod
    def get_type_name(cls, typeid):
        return cls._typemap2[typeid]

    name = CharField(
        max_length=255,
        null=False,
        help_text='Name of the message'
    )

    type = IntegerField(null=False, help_text='The type of the message (0, 1, 2, 3)')

    data = JsonField(null=False)
