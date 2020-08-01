from pyplanet.apps.config import AppConfig
from pyplanet.contrib.command import Command
from pyplanet.contrib.player.manager import Player
from pyplanet.contrib.setting import Setting
from pyplanet.apps.core.maniaplanet import callbacks as mp_signals
from pyplanet.contrib.map.exceptions import MapNotFound
from pyplanet.core.events import callback
from peewee import *
from pyplanet.core.db import TimedModel
from pyplanet.core.db.models.migration import Migration

from .models import Message, JsonField
from .view import SettingsView, MessagesView

import datetime
import logging
import functools
import asyncio


class Manialink(TimedModel):
    name = CharField(
        max_length=255,
        null=False,
        help_text='Name of the manialink'
    )

    type = TextField(null=False, default=None, help_text='The type of the entry (text, image or xml)')

    show = BooleanField(null=False, default=True, help_text='Specifies if the manialink should be shown or not')

    data = JsonField(null=False)


class Messages(AppConfig):
    name = 'messages'
    game_dependencies = ['trackmania', 'shootmania', 'trackmania_next']
    app_dependencies = ['core.maniaplanet']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.manialinks = None
        self.msg_view = MessagesView(self)
        self.msg_loop_task = None
        self.chat_messages = []
        self.msg_interval_setting = Setting('messages_interval', 'Messages interval', Setting.CAT_BEHAVIOUR, type=int,
                                            description='The time between the chat messages in seconds', default=60 * 5,
                                            change_target=self.interval_changed)
        self.loop = None
        self.lock = asyncio.Lock(loop=self.loop)
        self.msg_index = 0

    async def migrate_to_new_table(self):
        # Not using standard migrations because it would be skipped
        with self.instance.db.allow_sync():
            done_migrations = set(m.name for m in
                               Migration.select().where((Migration.app == Messages.name) & (Migration.applied == True)))
            if '000_messages_new_table' in done_migrations:
                # No need to migrate
                print('Already migrated')
                return
            if Manialink.table_exists():
                # No need to migrate
                mls = [ml for ml in Manialink.select().execute()]
                for ml in mls:  # type: Manialink
                    msg = Message(name=ml.name, type=Message.get_type_id(ml.type), data=ml.data, created_at=ml.created_at,
                                  updated_at=ml.updated_at)
                    Model.save(msg)
                Manialink.drop_table()
            else:
                print('Nothing to migrate')
            Migration.create(app=Messages.name, name='000_messages_new_table', applied=True)

    async def display(self, logins=None):
        if logins is None:
            await self.msg_view.refresh()
        else:
            await self.msg_view.display(player_logins=logins)

    async def hide_all(self):
        await self.msg_view.hide()

    async def reload(self, *args, **kwargs):
        await self.hide_all()
        await self.display()

    async def on_init(self):
        await super().on_init()
        await self.migrate_to_new_table()

    async def on_start(self):
        await super().on_start()
        await self.instance.permission_manager.register('admin', 'Administer the messages', app=self, min_level=3)
        await self.instance.command_manager.register(
            Command('messages', admin=True, target=self.show_setting_window, perms='messages:admin')
        )
        await self.context.setting.register(
            self.msg_interval_setting
        )

        self.context.signals.listen(mp_signals.map.map_start, self.map_start)
        self.context.signals.listen(mp_signals.flow.podium_start, self.on_map_end)
        self.context.signals.listen(mp_signals.player.player_connect, self.on_connect)
        self.manialinks = [ml for ml in await Message.execute(Message.select())]
        await self.manialinks_updated()
        await self.display()
        self.loop = asyncio.get_event_loop()
        self.msg_loop_task = asyncio.ensure_future(self.handle_messages(), loop=self.loop)
        await self.manialinks_updated()

    async def on_stop(self):
        await super().on_stop()

    async def on_destroy(self):
        await super().on_destroy()

    async def on_connect(self, player, *args, **kwargs):
        await self.display(logins=[player.login])

    async def on_map_end(self, *args, **kwargs):
        await self.hide_all()

    async def map_start(self, *args, **kwargs):
        await self.display()

    async def show_setting_window(self, player, *args, **kwargs):
        view = SettingsView(self, player)
        await view.show()

    async def manialinks_updated(self):
        try:
            await self.lock.acquire()
            self.chat_messages = [ml.data['raw_data'] for ml in self.manialinks if ml.type == 3]
        finally:
            self.lock.release()

    async def interval_changed(self, *args, **kwargs):
        if self.msg_loop_task is not None:
            self.msg_loop_task.cancel()
        # print('Restarted')
        self.msg_loop_task = asyncio.ensure_future(self.handle_messages(), loop=self.loop)

    async def handle_messages(self):
        # print('Started async')
        try:
            while True:
                interval = await self.msg_interval_setting.get_value()
                await asyncio.sleep(int(interval))
                try:
                    await self.lock.acquire()
                    if len(self.chat_messages) > 0:
                        self.msg_index %= len(self.chat_messages)
                        await self.instance.chat(self.chat_messages[self.msg_index])
                        self.msg_index += 1
                finally:
                    self.lock.release()
        except asyncio.CancelledError:
            pass
