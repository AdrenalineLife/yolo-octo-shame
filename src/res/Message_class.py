# -*- coding: utf-8 -*-
__author__ = 'Life'


class Message(object):
    def __init__(self, name, disp, msg, chan, color='', is_sub='0', is_mod='0', is_turbo='0', m_id=''):
        self.name = name.replace('\s', '')
        self.disp_name = disp.replace('\s', '') if disp else self.name
        self.message = msg
        self.chan = chan
        self.color = color
        self.is_mod = is_mod == '1'
        self.is_sub = is_sub == '1'
        self.is_turbo = is_turbo == '1'
        self.msg_id = m_id

    def __repr__(self):
        return '[{x.msg_id} s:{x.is_sub}, m:{x.is_mod}, t:{x.is_turbo} {x.chan}] <{x.disp_name}> {x.message}'.format(x=self)
