# -*- coding: utf-8 -*-
__author__ = 'Life'

import re


class Message(object):
    def __init__(self, data, expl=False, name=None, mes=None, chan_=None):
        if not expl:
            try:
                self.name = re.findall(r'@([a-zA-Z0-9_]+)[.]tmi[.]twitch[.]tv PRIVMSG', data)[0]
                self.disp_name = re.findall(r';display-name=([a-zA-Z0-9_]*)\\?[a-z]?;', data)[0]
                if not self.disp_name:
                    self.disp_name = self.name
                self.message = re.findall(r'@[a-zA-Z0-9_]+[.]tmi[.]twitch[.]tv PRIVMSG #[a-z0-9_]+ :(.*)', data)[0]
                self.chan = re.findall(r'@[a-zA-Z0-9_]+[.]tmi[.]twitch[.]tv PRIVMSG (.*?) :', data)[0]
                self.color = re.findall(r'^@color=([A-Z0-9#]*);', data)[0]
                self.is_mod = re.findall(r';mod=([01]);', data)[0] == '1'
                self.is_sub = re.findall(r';subscriber=([01]);', data)[0] == '1'
                self.is_turbo = re.findall(r';turbo=([01]);', data)[0] == '1'
            except IndexError as e:
                print('>>ERROR', e.args, '\n>>>', data)
        else:
            self.disp_name = name
            self.name = name
            self.message = mes
            self.chan = chan_
            self.color = ''
            self.is_mod = False
            self.is_sub = False
            self.is_turbo = False

    def __repr__(self):
        return 'sub: {}, mod: {} <{}> {}: {}'.format(self.is_sub, self.is_mod, self.chan, self.disp_name, self.message)