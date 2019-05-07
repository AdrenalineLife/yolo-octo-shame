# coding: utf-8

import time
import random

from src.res.MessageBase_class import MessageBase


class Usernotice(MessageBase):
    def __init__(self, name, display_name, msg, chan,
                 use_nonlatin_name=False, **kwargs):
        super().__init__(name, display_name, msg, chan, use_nonlatin_name=False, **kwargs)
        self.login = kwargs.get('login', '')
        self.msg_id = kwargs.get('msg_id', '')
        self.system_msg = kwargs.get('system_msg', '')

        tags = ('name', 'display_name', 'msg', 'chan', 'subscriber', 'color', 'mod', 'turbo', 'user_type',
                'id', 'user_id', 'room_id', 'sent_ts', 'tmi_sent_ts', 'emotes', 'badges')
        self.other_tags = {key: value for key, value in kwargs.items() if key not in tags}

    def is_sub(self):
        return self.msg_id in ('subgift', 'sub', 'resub', 'submysterygift', 'anonsubgift')


if __name__ == '__main__':
    pass