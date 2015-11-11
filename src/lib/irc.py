# -*- coding: utf-8 -*-
import socket, re, time, sys
from src.lib.functions_general import *
import src.lib.cron
import threading


class irc:
    def __init__(self, config, w=False):
        self.config = config
        self.whisper = w

    def check_for_message(self, data):
        if re.match(
                r'^:[a-zA-Z0-9_]+\![a-zA-Z0-9_]+@[a-zA-Z0-9_]+(\.tmi\.twitch\.tv|\.testserver\.local) PRIVMSG #[a-zA-Z0-9_]+ :.+$',
                data):
            return True

    def check_is_command(self, message, valid_commands):
        for command in valid_commands:
            if command == message:
                return True

    def check_for_connected(self, data):
        if re.match(r'^:.+ 001 .+ :connected to TMI$', data):
            return True

    def check_for_ping(self, data):
        if data[:4] == "PING":
            self.sock.send('PONG tmi.twitch.tv\r\n'.encode())
            #print('sending PONG')

    def get_message(self, data):
        return {
            'channel': re.findall(r'^:.+\![a-zA-Z0-9_]+@[a-zA-Z0-9_]+.+ PRIVMSG (.*?) :', data)[0],
            'username': re.findall(r'^:([a-zA-Z0-9_]+)\!', data)[0],
            'message': re.findall(r'PRIVMSG #[a-zA-Z0-9_]+ :(.+)', data)[0]
        }

    def check_login_status(self, data):
        if re.match(r'^:(testserver\.local|tmi\.twitch\.tv) NOTICE \* :Login unsuccessful\r\n$', data):
            return False
        else:
            return True

    def send_message(self, channel, message):
        self.sock.send('PRIVMSG {0} :{1}\n'.format(channel, message).encode())

    def send_whisper(self, message):
        self.sock.send('PRIVMSG #jtv :/w {0}\n'.format(message).encode())

    def get_irc_socket_object(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)  # default 10

        self.sock = sock
        serv = self.config['server_w'] if self.whisper else self.config['server']

        try:
            sock.connect((serv, self.config['port']))
        except:
            pp('Cannot connect to server (%s:%s).' % (serv, self.config['port']), 'error')
            if not self.whisper:
                sys.exit()

        sock.settimeout(None)

        sock.send('USER {0}\r\n'.format(self.config['username']).encode())
        sock.send('PASS {0}\r\n'.format(self.config['oauth_password']).encode())
        sock.send('NICK {0}\r\n'.format(self.config['username']).encode())

        if self.check_login_status(sock.recv(1024).decode()):
            pp('Login successful.')
        else:
            pp('Login unsuccessful. (hint: make sure your oauth token is set in self.config/self.config.py).', 'error')
            if not self.whisper:
                sys.exit()

        if self.whisper:
            sock.send('CAP REQ :twitch.tv/commands\r\n'.encode())

        # start threads for channels that have cron messages to run
        """for channel in self.config['channels']:
            if channel in self.config['cron']:
                if self.config['cron'][channel]['run_cron']:
                    thread.start_new_thread(cron.cron(self, channel).run, ())"""

        if not self.whisper:
            self.join_channels(self.channels_to_string(self.config['channels']))
        sock.settimeout(0)

        return sock

    def channels_to_string(self, channel_list):
        return ','.join(channel_list)

    def join_channels(self, channels):
        pp('Joining channels %s.' % channels)
        self.sock.send(('JOIN %s\r\n' % channels).encode())
        pp('Joined channels.')

    def leave_channels(self, channels):
        pp('Leaving chanels %s,' % channels)
        self.sock.send('PART {0}\r\n'.format(channels).encode())
        pp('Left channels.')
