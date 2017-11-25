# -*- coding: utf-8 -*-
__author__ = 'Life'

import re
import time


zalgo_chars = ('͑','͚','̧','͌','̈́','̈','̓','̉','͂','͙','͘','̦','͉','̍','͗','̃','̽','̩','͇','̭','̠','́','̟','̮','͡','͝',
               '̣','̹','ͩ','̼','̬','ͅ','͔','͆','̕','ͤ','̖','̶','͕','҉','ͣ','̛','̌','̙','̾','̓','͟','ͥ','͞','̞','ͮ','̥',
               '̋','̐','̨','̷','ͧ','ͪ','̄','͛','̝','͜','̒','̰','ͭ','̜','̲','̅','́','͠','̵','͢','̆','̀','̳','̢','̘','̀',
               '̗','͖','̔','̯','̚','ͬ','̂','̺','͈','̿','̎','̏','̊','͓','ͫ','ͨ','ͯ','̱','̡','ͦ','͋','͒','̫','̤','̻','̴',
               '͐','̇','͏','͍','͊','̸','͎','̑','̪')


def try_toint(x):
    try:
        return int(x)
    except ValueError:
        return x


class Message(object):
    def __init__(self, name, display_name, msg, chan,
                 use_nonlatin_name=False, **kwargs):

        self.created_ts = time.time()  # time when this object was created
        self.name = name.replace('\s', '')
        self.disp_name = display_name.replace('\s', ' ').strip() if display_name else self.name
        self.orig_disp_name = self.disp_name  # copy of original display name in case of changing "disp_name"

        if not use_nonlatin_name and not self.is_normal_disp_name():  # replace hieroglyphic disp_name if needed
            self.disp_name = self.name

        self.message = msg
        self.chan = chan  # chan name starts with '#'
        self.color = kwargs.get('color', '')
        self.is_mod = kwargs.get('mod', '0') == '1' or self.name == self.chan[1:]
        self.is_sub = kwargs.get('subscriber', '0') == '1'
        self.is_turbo = kwargs.get('turbo', '0') == '1'
        self.user_type = kwargs.get('user_type', '')
        self.msg_id = kwargs.get('id', '')
        self.user_id = kwargs.get('user_id', 0)
        self.chan_id = kwargs.get('room_id', 0)
        self.sent_ts = float(kwargs.get('sent_ts', 0.0)) / 1000.0  # unreliable, may be absent
        self.tmi_sent_ts = float(kwargs.get('tmi_sent_ts', 0.0)) / 1000.0  # unreliable, may be absent
        self.bits = int(kwargs.get('bits', 0))  # amount of bits which were sent

        # True if message uses "/me" command (all text is colored)
        self.uses_me = self.message.startswith("\x01ACTION") and self.message[-1] == "\x01"

        # removing special chars indicating about "/me"
        if self.uses_me:
            self.message = self.message[8:-1]

        # raw info about emotes
        self._emote_info = kwargs.get('emotes', '')
        # tuple of emotes' names in a msg; for internal usage only
        self._emotes = None

        # tuple of links in a msg; for internal usage only
        self._links = None

        badges = kwargs.get('badges', '')
        if badges:
            self.badges = {x.split('/')[0]: try_toint(x.split('/')[1]) for x in badges.split(',')}
        else:
            self.badges = {}

    # check if message is zalgo text
    def is_zalgo(self, threshold=25):
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

    @property  # am i doing this right ?
    def emotes(self):
        if self._emotes is None:  # then we calculate it
            if not self._emote_info:
                self._emotes = tuple()
                return self._emotes
            else:
                self._emotes = tuple(self.message[int(x.group(1)): int(x.group(2)) + 1] for x in
                                     re.finditer(r':(\d+)-(\d+)[,/]', self._emote_info + '/'))
                return self._emotes
        else:
            return self._emotes

    def __repr__(self):
        return '[s:{x.is_sub}, m:{x.is_mod}, t:{x.is_turbo} {x.chan}] <{x.disp_name}> {x.message}'.format(x=self)
