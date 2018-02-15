# -*- coding: utf-8 -*-

import socket
import re
import time
import sys
import threading

import src.lib.cron
from src.lib.functions_general import *


class IRC(socket.socket):
    def __init__(self, config):
        super().__init__(socket.AF_INET, socket.SOCK_STREAM)
        self.config = config
        self.resub_pat = re.compile(r'^@badges=.*?;msg-param-months=([0-9]+);.+msg-param-sub-plan=(.+?);.*?system-msg=(.+?)\\s.+? :tmi\.twitch\.tv USERNOTICE (#[a-zA-Z0-9_\\]+).*$')
        self.is_msg_pat = re.compile(r'^@badges=.*;user-type=.* :[a-zA-Z0-9_\\]+![a-zA-Z0-9_\\]+@[a-zA-Z0-9_\\]+(\.tmi\.twitch\.tv|\.testserver\.local) PRIVMSG #[a-zA-Z0-9_]+ :.+$')
        self.is_usernotice = re.compile(r'@.+ :tmi\.twitch\.tv USERNOTICE #[a-zA-Z0-9_\\]+.*$')

    @staticmethod
    def check_for_connected(data):
        return bool(re.match(r'^:.+ 001 .+ :connected to TMI$', data))

    def check_for_ping(self, data):
        if data[:4] == "PING":
            super().send('PONG tmi.twitch.tv\r\n'.encode())

    @staticmethod
    def check_login_status(data):
        return not bool(re.match(r'^:(testserver\.local|tmi\.twitch\.tv) NOTICE \* :Login unsuccessful\r\n$', data))

    def send_message(self, message, channel=None):
        super().send('PRIVMSG {} :{}\n'.format(channel, message).encode())

    def init_irc_socket_object(self, recnct_cnt=5):
        super().__init__(socket.AF_INET, socket.SOCK_STREAM)
        super().settimeout(10)  # default 10

        serv = self.config['server']

        try:
            super().connect((serv, self.config['port']))
        except Exception:
            if recnct_cnt > 0:
                pp('Cannot connect to server ({}:{}), trying again.'.format(serv, self.config['port']), mtype='error')
                super().close()
                time.sleep((5 - recnct_cnt)**2)
                return self.init_irc_socket_object(recnct_cnt=recnct_cnt - 1)
            else:
                pp('Cannot connect to server, exiting', mtype='ERROR')
                sys.exit()

        super().settimeout(None)

        super().send('USER {}\r\n'.format(self.config['username']).encode())
        super().send('PASS {}\r\n'.format(self.config['oauth_password']).encode())
        super().send('NICK {}\r\n'.format(self.config['username']).encode())

        if self.check_login_status(super().recv(1024).decode()):
            pp('Login successful')
        else:
            login_fail_msg = 'Login unsuccessful. (hint: make sure your oauth token is set in config.py)'
            pp(login_fail_msg, mtype='error')
            sys.exit()

        super().send('CAP REQ :twitch.tv/commands\r\n'.encode())
        super().send('CAP REQ :twitch.tv/tags\r\n'.encode())

        # NOT supported atm! start threads for channels that have cron messages to run
        """for channel in self.config['channels']:
            if channel in self.config['cron']:
                if self.config['cron'][channel]['run_cron']:
                    thread.start_new_thread(cron.cron(self, channel).run, ())"""

        self.join_channels(self.channels_to_string(self.config['channels']))
        super().settimeout(0)

    @staticmethod
    def channels_to_string(channel_list):
        return ','.join(channel_list)

    def join_channels(self, channels):
        pp('Joining channels {}'.format(channels))
        super().send(('JOIN {}\r\n'.format(channels)).encode())
        pp('Joined channels')

    def leave_channels(self, channels):
        pp('Leaving chanels {},'.format(channels))
        super().send('PART {}\r\n'.format(channels).encode())
        pp('Left channels')

    def check_for_message(self, data):
        return bool(self.is_msg_pat.match(data))

    def parse_message(self, msg):
        first, sec = msg.split(' PRIVMSG ', maxsplit=1)
        tags, name = first.split(' :')
        name = name.split('!')[0]
        chan, message = sec.split(' :', maxsplit=1)
        # tags = {x.split('=')[0].replace('-','_'): x.split('=')[1] for x in tags.lstrip('@').split(';')}
        itr = (x.split('=') for x in tags.lstrip('@').split(';'))
        tags = {key.replace('-', '_'): value for key, value in itr}
        tags.update(name=name, chan=chan, msg=message)
        return tags

    def parse_usernotice(self, msg):
        first, sec = msg.split(' USERNOTICE ', maxsplit=1)
        tags = first.split(' :')[0]
        if ':' in sec:
            chan, message = sec.split(' :', maxsplit=1)
        else:
            chan, message = sec, ''
        itr = (x.split('=') for x in tags.lstrip('@').split(';'))
        tags = {key.replace('-', '_'): value for key, value in itr}
        tags.update(chan=chan, msg=message)
        return tags

    def check_for_sub(self, usernotice):
        return usernotice.get('msg_id') in ('subgift', 'sub', 'resub')
