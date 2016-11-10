# -*- coding: utf-8 -*-
"""
Simple IRC Bot for Twitch.tv
Developed by Aidan Thomson <aidraj0@gmail.com>
"""

import re
import importlib
import threading
import requests
import random
import traceback
import json

import src.lib.irc as irc_
import src.lib.command_headers as headers
from src.lib.functions_general import *
from src.res.Message_class import Message
from src.res.Channel_class import Channel


class Roboraj(object):
    def __init__(self, config):
        self.config = config
        self.irc = irc_.Irc(config)
        self.msg_pat = re.compile(r'@badges=(.*?);color=(.*);display-name=(.*?);emotes=(.*?);id=([a-zA-Z0-9-]*);mod=([01]);room-id=.*?subscriber=([01]);.*?turbo=([01]);user-id=.* :([a-zA-Z0-9_\\]*)!.*@.*tmi\.twitch\.tv PRIVMSG (#[a-zA-Z0-9_\\]+) :(.*)')
        self.resub_pat = re.compile(r'^@badges=.*emotes=.*;msg-id=resub;msg-param-months=([0-9]+);.+system-msg=(.+?)\\s.+ :tmi\.twitch\.tv USERNOTICE (#[a-zA-Z0-9_\\]+).*')
        self.sub_pat = re.compile(r':twitchnotify!twitchnotify@twitchnotify[.]tmi[.]twitch[.]tv PRIVMSG (#[a-zA-Z0-9_]+) :(.+?) just subscribed!')
        self.is_msg_pat = re.compile(r'.*;color=.*;user-type=.* :[a-zA-Z0-9_\\]+![a-zA-Z0-9_\\]+@[a-zA-Z0-9_\\]+(\.tmi\.twitch\.tv|\.testserver\.local) PRIVMSG #[a-zA-Z0-9_]+ :.+$')

        # list of channels (rooms)
        self.ch_list = list()

        # info about commands (dict)
        self.cmd_headers = headers.commands

        # headers for all api requests
        self.req_headers = {'Client-ID': self.config['Client-ID']}

        # session for api requests to get streams info
        self.chans_request = requests.Session()
        self.chans_request.headers = self.req_headers
        self.chans_request.params = {'channel': ','.join(x[1:] for x in self.config['channels'])}

    def check_for_message(self, data):
        return bool(self.is_msg_pat.match(data))

    def parse_message(self, msg):
        try:
            r = self.msg_pat.findall(msg)[0]
        except IndexError:
            print('>'*10, '\n', msg)
            return '*ERROR*', '', '', '#', '', '0', '0', '0', ''
        # order: name, disp_name, msg, chan, color, is_sub, is_mod, is_turbo, id, emote_info, badge_info
        return r[8], r[2], r[10], r[9], r[1], r[6], r[5], r[7], r[4], r[3], r[0]

    def load_or_create_channel_list(self):
        try:
            self.ch_list = load_obj('history')
        except FileNotFoundError:
            self.ch_list = [Channel(x.lstrip('#'), self.req_headers) for x in self.config['channels']]
        except Exception:
            self.ch_list = [Channel(x.lstrip('#'), self.req_headers) for x in self.config['channels']]
            pp("Could not load channel file", 'error')
        else:
            # deleting unnacessery channels
            self.ch_list[:] = [x for x in self.ch_list if '#' + x.name in self.config['channels']]
            loaded_ch = [x.name for x in self.ch_list]

            # adding missing channels
            for x in self.config['channels']:
                if x.lstrip('#') not in loaded_ch:
                    self.ch_list.append(Channel(x.lstrip('#'), self.req_headers))
            del loaded_ch

    def load_command_funcs(self):
        for channel in self.config['channels']:
            for command in self.cmd_headers:
                self.cmd_headers[command]['time'] = 0
                self.cmd_headers[command][channel] = {}
                self.cmd_headers[command][channel]['last_used'] = 0

        missing_func = []
        for command in self.cmd_headers:
            if self.cmd_headers[command]['return'] == 'command':
                try:
                    module = importlib.import_module('src.lib.commands.' + command[1:])
                    setattr(self.__class__, command, getattr(module, command[1:]))
                except ImportError:
                    missing_func.append(command)
                    pp('No module found: ' + command, 'warning')
                except AttributeError:
                    missing_func.append(command)
                    pp('No function found: ' + command, 'warning')
            if 'return' not in self.cmd_headers[command] or not self.cmd_headers[command]['return']:
                missing_func.append(command)

        # deleting commands from dict which we did not find
        for f in missing_func:
            self.cmd_headers.pop(f, None)

    def call_func(self, command, args, msg):
        return getattr(self, command)(args, msg)

    def is_valid_command(self, command):
        return command in self.cmd_headers

    def has_correct_args(self, message, command):
        qty = len(message.split(' ')) - 1
        return self.cmd_headers[command]['argc_min'] <= qty <= self.cmd_headers[command]['argc_max']

    def is_on_cooldown(self, command, channel):
        return time.time() - self.cmd_headers[command][channel]['last_used'] < self.cmd_headers[command]['limit']

    def get_cooldown_remaining(self, command, channel):
        return round(self.cmd_headers[command]['limit'] - (time.time() - self.cmd_headers[command][channel]['last_used']))

    def update_last_used(self, command, channel):
        self.cmd_headers[command][channel]['last_used'] = time.time()

    def check_channel_state(self):
        while True:
            try:
                resp = self.chans_request.get('https://api.twitch.tv/kraken/streams', timeout=5.0)
                if resp.status_code != 200:
                    time.sleep(4.0)
                    continue
                resp = resp.json()['streams']
            except (requests.RequestException, ValueError):
                time.sleep(4.0)
                continue
            except KeyError:
                pp("There is no 'streams' key in API response", mtype='ERROR')
                time.sleep(4.0)
                continue
            #print(json.dumps(resp, indent=4))

            for ch in self.ch_list:
                chan_info = [x for x in resp if x['channel']['name'] == ch.name]
                chan_info = chan_info[0] if chan_info else None
                try:
                    ch.get_state(chan_info)
                except KeyError:
                    pp('Failed getting channel state', mtype='error')
                    continue
                if ch.is_online:
                    ch.add_game()
                    ch.started = True
                else:
                    if ch.started:
                        ch.games[-1]['ended'] = time.time()
                        ch.time_ = time.time()
                        ch.max_viewers = 0
                        ch.started = False
                    if ch.expired():
                        ch.games = []
            save_obj(self.ch_list, 'history')
            time.sleep(9.0)

    def send_to_chat(self, result, username='', channel=''):
        resp = result.replace('(sender)', username)
        channel = '#jtv' if result.startswith('/w ') else channel
        pbot(resp, channel)
        self.irc.send_message(resp, channel)

    def check_for_sub(self, msg):
        res = self.resub_pat.search(msg) or self.sub_pat.search(msg)
        if res:
            res = res.groups()
        else:
            return tuple()
        # in case of new sub, month = 0
        return (res[0], res[1].replace('\s', ''), 0) if len(res) == 2 else (res[2], res[1], int(res[0]))

    def sub_greetings(self, sub_info):
        if not sub_info:
            return None
        resp = self.call_func('!sub_greetings', sub_info, None)
        if resp:
            if type(resp) == list:
                for r in resp:
                    self.send_to_chat(r, channel=sub_info[0])
            else:
                self.send_to_chat(resp, channel=sub_info[0])
        self.cmd_headers['!sub_greetings']['time'] = time.time()

    def run(self):
        config = self.config
        if not config['oauth_password'].startswith('oauth:'):
            pp("OAuth password should start with 'oauth:'", mtype='error')

        self.irc.get_irc_socket_object()
        self.load_or_create_channel_list()
        self.load_command_funcs()

        try:
            if requests.get('https://api.twitch.tv/kraken', headers=self.req_headers, timeout=5).json()['identified']:
                pp('Your Client-ID is ok, you can use api calls')
            else:
                pp('Your Client-ID is not identified, your api calls will fail', 'warning')
        except KeyError:
            pp("There is no 'identified' key, client id wasn't checked", mtype='WARNING')
        except Exception:
            pp("Client ID wasn't checked", mtype='WARNING')

        trd = threading.Thread(target=self.check_channel_state, args=())
        trd.start()

        say_cd = '/w (sender) Команда будет доступна через {} сек'
        pbot_on_cd = 'Command is on cooldown. ({}) ({}) ({}s remaining)'
        pbot_not_on_cd = 'Command is valid and not on cooldown. ({}) ({})'

        while True:
            time.sleep(0.003)
            try:
                data = self.irc.recv(config['socket_buffer_size']).decode().rstrip()
            except Exception:
                data = 'empty'

            if len(data) == 0:
                pp('Connection was lost, reconnecting.')
                self.irc.get_irc_socket_object()

            if time.time() - self.cmd_headers['!ragnaros']['time'] >= 7:
                self.cmd_headers['!ragnaros']['time'] = time.time()
                for ch in config['channels']:
                    for r in self.call_func('!ragnaros', ['check'], Message('', '', '', ch)):
                        self.send_to_chat(r, channel=ch)

            if time.time() - self.cmd_headers['!duel']['time'] >= 5:
                for ch in config['channels']:
                    for duel_resp in self.call_func('!duel', ['chk'], Message('', '', '', ch)):
                        self.send_to_chat(duel_resp, channel=ch)
                self.cmd_headers['!duel']['time'] = time.time()

            for data_line in data.split('\r\n'):
                if config['debug'] and data_line != 'empty':
                    print(data_line)

                self.irc.check_for_ping(data_line)
                self.sub_greetings(self.check_for_sub(data_line))

                if self.check_for_message(data_line):
                    msg = Message(*self.parse_message(data_line))

                    ##### RANDOM CUSTOM STUFF

                    ##### END OF RANDOM CUSTOM STUFF

                    if not config['debug']:
                        ppi(msg.chan, msg.message, msg.disp_name)

                    self.call_func('!ragnaros', ['add'], msg)

                    if self.is_valid_command(msg.message.split(' ')[0]):
                        command = msg.message
                        command_name = command.split(' ')[0]

                        if self.cmd_headers[command_name]['return'] == 'command':
                            if self.has_correct_args(command, command_name):
                                args = command.split(' ')
                                del args[0]

                                if self.is_on_cooldown(command_name, msg.chan):
                                    sec_remaining = self.get_cooldown_remaining(command_name, msg.chan)
                                    self.send_to_chat(say_cd.format(sec_remaining), msg.disp_name, msg.chan)
                                    pbot(pbot_on_cd.format(command_name, msg.disp_name, sec_remaining), msg.chan)
                                else:
                                    pbot(pbot_not_on_cd.format(command_name, msg.disp_name), msg.chan)

                                    result = self.call_func(command_name, args, msg)

                                    if result:
                                        if type(result) == list:
                                            for r in result:
                                                self.send_to_chat(r, msg.disp_name, msg.chan)
                                        else:
                                            self.send_to_chat(result, msg.disp_name, msg.chan)
                                        self.update_last_used(command_name, msg.chan)
                            else:
                                pp("Invalid number of arguments for '{}'".format(command_name))

                        else:
                            if self.is_on_cooldown(command_name, msg.chan):
                                sec_remaining = self.get_cooldown_remaining(command_name, msg.chan)
                                self.send_to_chat(say_cd.format(sec_remaining), msg.disp_name, msg.chan)
                                pbot(pbot_on_cd.format(command_name, msg.disp_name, sec_remaining), msg.chan)
                            else:
                                pbot(pbot_not_on_cd.format(command_name, msg.disp_name), msg.chan)
                                resp = self.cmd_headers[command_name]['return']
                                self.update_last_used(command_name, msg.chan)
                                self.send_to_chat(resp, msg.disp_name, msg.chan)
