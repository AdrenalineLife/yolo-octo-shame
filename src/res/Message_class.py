# -*- coding: utf-8 -*-
__author__ = 'Life'

import re
import traceback
from src.lib.functions_general import *

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
                self.is_mod = (re.findall(r';mod=([01]);', data)[0] == '1') or (self.chan[1:] == self.name)
                self.is_sub = re.findall(r';subscriber=([01]);', data)[0] == '1'
                self.is_turbo = re.findall(r';turbo=([01]);', data)[0] == '1'
            except Exception as ee:
                err_msg = data + '\n' + traceback.format_exc()
                pp('PARSING ERROR, look at error_traceback.txt', 'ERROR')
                f_ = open('error_traceback.txt', 'at')
                f_.write(err_msg + '______________________\n')
                f_.close()
                self.name, self.disp_name, self.chan, self.message = '', '', '#', ''
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
        return '[s:{x.is_sub}, m:{x.is_mod} {x.chan}] <{x.disp_name}> {x.message}'.format(x=self)