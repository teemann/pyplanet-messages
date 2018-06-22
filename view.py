from pyplanet.views.generics import ManualListView
from pyplanet.views import TemplateView
from pyplanet.views.generics import ask_confirmation
from .models import Message


class SettingsView(ManualListView):
    title = 'Manialinks'
    icon_style = 'Icons128x128_1'
    icon_substyle = 'Manialink'

    def __init__(self, app, player):
        super().__init__(self)
        self.fields = self._create_fields()
        self.objects_raw = []
        self.app = app
        self.player = player
        self.manager = app.context.ui
        self.buttons = self._create_buttons()
        self.actions = self._create_actions()
        self.sort_field = self.fields[1]
        self.fill_data()

    def fill_data(self):
        self.objects_raw.clear()
        for ml in self.app.manialinks:
            self.objects_raw.append({'name': ml.name, 'type': Message.get_type_name(ml.type), 'data': ml})

    async def show(self):
        await self.display(player=self.player)

    def _create_fields(self):
        return [
            {
                'name': 'Type',
                'index': 'type',
                'sorting': True,
                'searching': True,
                'width': 30,
                'type': 'label',
            },
            {
                'name': 'Name',
                'index': 'name',
                'sorting': True,
                'searching': True,
                'width': 110,
                'type': 'label'
            },
        ]

    def _create_buttons(self):
        return [
            {
                'title': 'New',
                'width': 10,
                'action': self.add_basic_action
            }
        ]

    def _create_actions(self):
        return [
            dict(
                name='edit',
                action=self.edit,
                text='&#xF013;',
                textsize=1.2,
                safe=True,
                type='label',
                order=0,
                require_confirm=False,
            ),
            dict(
                name='delete',
                action=self.delete,
                text='&#xF1F8;',
                textsize=1.2,
                safe=True,
                type='label',
                order=0,
                require_confirm=False,
            )
        ]

    async def manialinks_updated(self):
        await self.app.display()
        await self.app.manialinks_updated()

    async def get_actions(self):
        if len(self.objects_raw) == 0:
            return []
        return self.actions

    async def edit(self, player, values, instance, **kwargs):
        # print('edit', locals())
        view = NewMessageView(self, self.app, manialink=instance['data'])
        await view.display(player_logins=[player.login])
        await self.manialinks_updated()

    async def delete(self, player, values, instance, **kwargs):
        # print('delete', locals())
        cancel = bool(
            await ask_confirmation(player, 'Do you really want to delete the message {}?'.format(instance['name']))
        )
        if not cancel:
            self.app.manialinks.remove(instance['data'])
            await instance['data'].destroy()
            self.fill_data()
            await self.display(player=player)
            await self.manialinks_updated()

    async def add_basic_action(self, player, *args, **kwargs):
        # print('add_basic', locals())
        msg = NewMessageView(self, self.app)
        await msg.display(player_logins=[player.login])

    async def get_data(self):
        if len(self.objects_raw) == 0:
            return [{'type': '', 'name': 'Empty'}]
        # print(self.objects_raw)
        return self.objects_raw

    async def add_manialink(self, name, type, data, manialink=None):
        if manialink is not None:
            manialink.data = data
            manialink.type = type
            manialink.name = name
            await manialink.save()
        else:
            ml = Message(name=name, type=type, data=data)
            await ml.save()
            self.app.manialinks.append(ml)
        self.fill_data()
        await self.display(self.player)
        await self.manialinks_updated()


class NewMessageView(TemplateView):
    template_name = 'messages/edit.xml'

    def __init__(self, parent, app, *args, manialink=None, **kwargs):
        self.id = 'manialink_newmessage'
        super().__init__(app.context.ui, *args, **kwargs)
        self.parent = parent
        self.manialink = manialink
        self.subscribe('cancel', self.cancelled)
        self.subscribe('ok', self.ok_event)

    async def get_context_data(self):
        data = await super().get_context_data()
        data.update({
            'id': self.id,
            'dlg_type': 'New',
            'name': '',
            'posx': '',
            'posy': '',
            'posz': '',
            'value': '',
            'type_id': 0,
            'link': '',
            'aspect': '1'
        })
        if self.manialink is not None:
            pos = self.manialink.data.get('pos', [0, 0, 0])
            size = self.manialink.data.get('size', None)
            if size is None:
                size = ['', '']
            type_id = self.manialink.type
            data.update({
                'dlg_type': 'Edit',
                'name': self.manialink.name,
                'posx': pos[0],
                'posy': pos[1],
                'posz': pos[2],
                'value': self.manialink.data.get('raw_data', ''),
                'type_id': type_id,
                'link': self.manialink.data.get('link', ''),
                'wid': size[0],
                'hei': size[1],
                'aspect': self.manialink.data.get('aspect', '1')
            })
        # print('___GET_CONTEXT_DATA_____', data)
        return data

    async def cancelled(self, player, action, values, **kwargs):
        await self.hide(player_logins=[player.login])

    async def ok_event(self, player, action, values, **kwargs):
        await self.hide(player_logins=[player.login])
        pos = [values['messages_pos_x'], values['messages_pos_y'], values['messages_pos_z']]
        data = values.get('messages_value', '')
        msg_type = int(values.get('messages_type_value', ''))
        link = values.get('messages_link', '')
        size = [values['messages_size_w'], values['messages_size_h']]
        aspect = values['messages_aspect_value']
        if len(size[0]) == 0 or len(size[1]) == 0:
            size = None
        # print(pos, data, link, msg_type)
        ml_data = {
            'pos': pos,
            'link': link,
            'data': self._render(msg_type, data, link, pos, size, aspect == '1'),
            'size': size,
            'raw_data': data,
            'aspect': aspect
        }
        await self.parent.add_manialink(values.get('messages_name', ''), msg_type,
                                        ml_data, self.manialink)

    def _render(self, type, data, link, pos, size=None, aspect=True):
        # print('"{}"'.format(type))
        if type == 0:
            attrs = 'pos="{} {}" z-index="{}" text="{}" class="distraction-hide"'.format(*pos, data)
            if link is not None and len(link) != 0:
                attrs += ' url="{}"'.format(link)
            return '<label {}/>'.format(attrs)
        elif type == 1:
            attrs = 'pos="{} {}" z-index="{}" image="{}" halign="center" valign="center" class="distraction-hide"'\
                .format(*pos, data)
            if link is not None and len(link) != 0:
                attrs += ' url="{}"'.format(link)
            if size is not None:
                attrs += ' size="{} {}"'.format(*size)
            if aspect:
                attrs += ' keepratio="Fit"'
            return '<quad {}/>'.format(attrs)
        elif type == 2:
            return '<frame>{}</frame>'.format(data)
        return ''


class MessagesView(TemplateView):
    template_name = 'messages/messages.xml'

    def __init__(self, app, *args, **kwargs):
        self.id = 'manialinks_messages'
        super().__init__(app.context.ui, *args, **kwargs)
        self.app = app

    async def refresh(self):
        await self.display()

    async def get_context_data(self):
        manialinks = [ml.data.get('data', '') for ml in self.app.manialinks]
        data = await super().get_context_data()
        data.update({
            'id': self.id,
            'manialinks': manialinks
        })
        # print('___________________________________________________DISPLAY_____', data)
        return data
