# -*- coding: utf-8 -*-
__author__ = 'Life'

import re


zalgo_chars = ('͑','͚','̧','͌','̈́','̈','̓','̉','͂','͙','͘','̦','͉','̍','͗','̃','̽','̩','͇','̭','̠','́','̟','̮','͡','͝',
               '̣','̹','ͩ','̼','̬','ͅ','͔','͆','̕','ͤ','̖','̶','͕','҉','ͣ','̛','̌','̙','̾','̓','͟','ͥ','͞','̞','ͮ','̥',
               '̋','̐','̨','̷','ͧ','ͪ','̄','͛','̝','͜','̒','̰','ͭ','̜','̲','̅','́','͠','̵','͢','̆','̀','̳','̢','̘','̀',
               '̗','͖','̔','̯','̚','ͬ','̂','̺','͈','̿','̎','̏','̊','͓','ͫ','ͨ','ͯ','̱','̡','ͦ','͋','͒','̫','̤','̻','̴',
               '͐','̇','͏','͍','͊','̸','͎','̑','̪')


class Message(object):
    def __init__(self, name, disp, msg, chan,
                 color='', is_sub='0', is_mod='0', is_turbo='0', m_id='', emote_info='', badge_info='',
                 use_nonlatin_name=False):
        self.name = name.replace('\s', '')
        self.disp_name = disp.replace('\s', '') if disp else self.name
        self.orig_disp_name = self.disp_name  # copy of original display name in case of changing "disp_name"

        if not use_nonlatin_name and not self.is_normal_disp_name():
            self.disp_name = self.name

        self.message = msg
        self.chan = chan
        self.color = color
        self.is_mod = is_mod == '1' or self.name == self.chan[1:]
        self.is_sub = is_sub == '1'
        self.is_turbo = is_turbo == '1'
        self.msg_id = m_id

        # True if message uses "/me" command (all text is colored)
        self.uses_me = self.message.startswith("\x01ACTION") and self.message[-1] == "\x01"

        # removing special chars indicating about "/me"
        if self.uses_me:
            self.message = self.message[8:-1]

        self.__emote_info__ = emote_info
        self.__badge_info__ = badge_info

    def is_zalgo(self, threshold=40):
        if len(self.message) < threshold:
            return False
        cnt = 0
        for char in self.message:
            if char in zalgo_chars:
                cnt += 1
            if cnt >= threshold:
                return True
        return False

    def is_normal_disp_name(self):
        return bool(re.match(r'^[a-zA-Z0-9_\\]+$', self.disp_name))

    def emotes(self):
        if not self.__emote_info__:
            return tuple()
        return tuple(self.message[int(x.group(1)): int(x.group(2)) + 1] for x in
                     re.finditer(r':(\d+)-(\d+)[,/]', self.__emote_info__ + '/'))

    def __repr__(self):
        return '[s:{x.is_sub}, m:{x.is_mod}, t:{x.is_turbo} {x.chan}] <{x.disp_name}> {x.message}'.format(x=self)
