from pyplanet.apps.config import AppConfig
from pyplanet.contrib.command import Command
from pyplanet.contrib.player.manager import Player
from pyplanet.contrib.setting import Setting
from pyplanet.apps.core.maniaplanet import callbacks as mp_signals
from pyplanet.contrib.map.exceptions import MapNotFound
from pyplanet.core.events import callback

from .models import Manialink
from .view import SettingsView, MessagesView

import datetime
import logging
import functools


class Messages(AppConfig):
    name = 'messages'
    game_dependencies = ['trackmania', 'shootmania']
    app_dependencies = ['core.maniaplanet']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.manialinks = None
        self.msg_view = MessagesView(self)

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

    async def on_start(self):
        await super().on_start()
        await self.instance.permission_manager.register('admin', 'Administer the messages', app=self, min_level=3)
        await self.instance.command_manager.register(
            Command('messages', admin=True, target=self.show_setting_window, perms='messages:admin')
        )

        self.instance.signal_manager.listen(mp_signals.map.map_start, self.map_start)
        self.instance.signal_manager.listen(mp_signals.flow.podium_start, self.on_map_end)
        self.instance.signal_manager.listen(mp_signals.player.player_connect, self.on_connect)
        self.manialinks = [ml for ml in await Manialink.execute(Manialink.select())]
        await self.display()

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

    async def add_manialink(self, manialink):
        pass