# -*- coding: utf-8 -*-

import socket
import re
import time
import sys
import threading

import src.lib.cron
from src.lib.functions_general import *


class Irc(socket.socket):
    def __init__(self, config, w=False):
        super().__init__(socket.AF_INET, socket.SOCK_STREAM)
        self.config = config
        self.whisper = w

    @staticmethod
    def check_for_message(data):
        return bool(re.match(
            r'^@color=.*;user-type=.* :[a-zA-Z0-9_]+![a-zA-Z0-9_]+@[a-zA-Z0-9_]+(\.tmi\.twitch\.tv|\.testserver\.local) PRIVMSG #[a-zA-Z0-9_]+ :.+$',
            #r'^:[a-zA-Z0-9_]+\![a-zA-Z0-9_]+@[a-zA-Z0-9_]+(\.tmi\.twitch\.tv|\.testserver\.local) PRIVMSG #[a-zA-Z0-9_]+ :.+$',
            data))

    @staticmethod
    def check_is_command(message, valid_commands):
        for command in valid_commands:
            if command == message:
                return True

    @staticmethod
    def check_for_connected(data):
        return bool(re.match(r'^:.+ 001 .+ :connected to TMI$', data))

    def check_for_ping(self, data):
        if data[:4] == "PING":
            super().send('PONG tmi.twitch.tv\r\n'.encode())
            #print('sending PONG')

    @staticmethod
    def check_login_status(data):
        return not bool(re.match(r'^:(testserver\.local|tmi\.twitch\.tv) NOTICE \* :Login unsuccessful\r\n$', data))

    def send_message(self, channel, message):
        super().send('PRIVMSG {0} :{1}\n'.format(channel, message).encode())

    def send_whisper(self, message):
        super().send('PRIVMSG #jtv :{0}\n'.format(message).encode())

    def get_irc_socket_object(self):
        super().settimeout(10)  # default 10

        serv = self.config['server_w'] if self.whisper else self.config['server']

        try:
            super().connect((serv, self.config['port']))
        except Exception:
            pp('Cannot connect to server ({}:{}).'.format(serv, self.config['port']), 'error')
            if not self.whisper:
                sys.exit()

        super().settimeout(None)

        super().send('USER {}\r\n'.format(self.config['username']).encode())
        super().send('PASS {}\r\n'.format(self.config['oauth_password']).encode())
        super().send('NICK {}\r\n'.format(self.config['username']).encode())

        whisper_msg = 'to whisper server ' if self.whisper else ''
        if self.check_login_status(super().recv(1024).decode()):
            pp('Login {}successful.'.format(whisper_msg))
        else:
            login_fail_msg = 'Login {}unsuccessful. (hint: make sure your oauth token is set in self.config/self.config.py).'
            pp(login_fail_msg.format(whisper_msg), 'error')
            if not self.whisper:
                sys.exit()

        if self.whisper:
            super().send('CAP REQ :twitch.tv/commands\r\n'.encode())
        else:
            super().send('CAP REQ :twitch.tv/tags\r\n'.encode())

        # start threads for channels that have cron messages to run
        """for channel in self.config['channels']:
            if channel in self.config['cron']:
                if self.config['cron'][channel]['run_cron']:
                    thread.start_new_thread(cron.cron(self, channel).run, ())"""

        if not self.whisper:
            self.join_channels(self.channels_to_string(self.config['channels']))
        super().settimeout(0)

    @staticmethod
    def channels_to_string(channel_list):
        return ','.join(channel_list)

    def join_channels(self, channels):
        pp('Joining channels {}'.format(channels))
        super().send(('JOIN {}\r\n'.format(channels)).encode())
        pp('Joined channels.')

    def leave_channels(channels):
        pp('Leaving chanels {},'.format(channels))
        super().send('PART {0}\r\n'.format(channels).encode())
        pp('Left channels.')
