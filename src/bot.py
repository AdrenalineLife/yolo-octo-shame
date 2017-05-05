# -*- coding: utf-8 -*-
"""
Simple IRC Bot for Twitch.tv
Developed by Aidan Thomson <aidraj0@gmail.com>
"""

import re
import importlib
import threading
import requests
import json
from collections import deque

import src.lib.irc as irc_
import src.lib.command_headers as c_headers
from src.lib.functions_general import *
from src.res.Message_class import Message
from src.res.Channel_class import Channel
from src.res.CommandHandler_class import CommandHandler


class Roboraj(object):
    def __init__(self, config):
        self.config = config
        self.irc = irc_.Irc(config)
        #self.msg_pat = re.compile(r'@badges=(.*?);color=(.*);display-name=(.*?);emotes=(.*?);id=([a-zA-Z0-9-]*);mod=([01]);room-id=.*?subscriber=([01]);.*?turbo=([01]);user-id=.* :([a-zA-Z0-9_\\]*)!.*@.*tmi\.twitch\.tv PRIVMSG (#[a-zA-Z0-9_\\]+) :(.*)')
        self.resub_pat = re.compile(r'^@badges=.*?;msg-id=resub;msg-param-months=([0-9]+);.+system-msg=(.+?)\\s.*?with\\s(Twitch\\sPrime)?.+ :tmi\.twitch\.tv USERNOTICE (#[a-zA-Z0-9_\\]+).*$')
        self.sub_pat = re.compile(r':twitchnotify!twitchnotify@twitchnotify\.tmi\.twitch\.tv PRIVMSG (#[a-zA-Z0-9_]+) :(.+?) just subscribed with (Twitch Prime)?!')
        self.is_msg_pat = re.compile(r'^@badges=.*;user-type=.* :[a-zA-Z0-9_\\]+![a-zA-Z0-9_\\]+@[a-zA-Z0-9_\\]+(\.tmi\.twitch\.tv|\.testserver\.local) PRIVMSG #[a-zA-Z0-9_]+ :.+$')

        # list of channels
        self.ch_list = list()

        # info about commands
        self.cmd_headers = CommandHandler(c_headers.commands)

        # pass
        self.chat_messages = {chan: deque(maxlen=300) for chan in self.config['channels']}

        # headers for all API requests
        self.req_headers = {'Client-ID': self.config['Client-ID'],
                            'Accept': "application/vnd.twitchtv.v3+json"}

        # boolean to indicate if Client-ID if identified
        self.clientid_identified = False

        # session for API requests to get streams info
        self.chans_request = requests.Session()
        self.chans_request.headers = self.req_headers
        self.chans_request.params = {'channel': ','.join(x[1:] for x in self.config['channels'])}

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

    def load_or_create_channel_list(self):
        try:
            self.ch_list = load_obj('channel_list')
        except FileNotFoundError:
            self.ch_list = [Channel(x.lstrip('#'), self.req_headers) for x in self.config['channels']]
        except Exception:
            self.ch_list = [Channel(x.lstrip('#'), self.req_headers) for x in self.config['channels']]
            pp("Could not load channel file", mtype='ERROR')
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
        missing_func = []
        for cmd_name, command in self.cmd_headers.items():
            if 'ref' not in command:
                if command['return'] == 'command':
                    try:
                        module = importlib.import_module('src.lib.commands.' + cmd_name[1:])
                        setattr(self.__class__, cmd_name, getattr(module, cmd_name[1:]))
                    except ImportError:
                        missing_func.append(cmd_name)
                        pp('No module found: ' + cmd_name, mtype='WARNING')
                    except AttributeError:
                        missing_func.append(cmd_name)
                        pp('No function found: ' + cmd_name, mtype='WARNING')
                if 'return' not in command or not command['return']:
                    pp("'" + cmd_name + "' command does not have 'return'", mtype='WARNING')
                    missing_func.append(cmd_name)

        # deleting commands from dict which we did not find
        for f in missing_func:
            self.cmd_headers.pop(f, None)

        for cmd_name in self.cmd_headers:
            if 'ref' not in self.cmd_headers[cmd_name]:
                for channel in self.config['channels']:
                    self.cmd_headers[cmd_name]['time'] = 0.0
                    self.cmd_headers[cmd_name]['name'] = cmd_name
                    self.cmd_headers[cmd_name][channel] = {}
                    self.cmd_headers[cmd_name][channel]['last_used'] = 0.0
                    self.cmd_headers[cmd_name][channel]['last_used_name'] = ''

        missing_func[:] = []
        for cmd_name, command in self.cmd_headers.items():
            if 'ref' in command:
                if command['ref'] in self.cmd_headers:
                    self.cmd_headers[cmd_name] = self.cmd_headers[command['ref']]
                else:
                    pp("Unresolved reference: {}".format(command['ref']), mtype='WARNING')
                    missing_func.append(cmd_name)
        for f in missing_func:
            self.cmd_headers.pop(f, None)

    def call_func(self, command, args, msg):
        return getattr(self, command)(args, msg)

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
                        ch.started = False
                    if ch.expired():
                        ch.games = []
                        ch.max_viewers = 0
                        ch.created_at_withbreak = ''
            save_obj(self.ch_list, 'channel_list')
            time.sleep(9.0)

    def send_to_chat(self, result, username='', channel=''):
        resp = result.replace('(sender)', username)
        channel = '#jtv' if result.startswith('/w ') else channel
        self.irc.send_message(resp, channel)
        pbot(resp, channel)

    # check if client id is identified
    def check_client_id(self, retries=3):
        cnt = 1
        while cnt <= retries:
            try:
                r = requests.get('https://api.twitch.tv/kraken/', headers=self.req_headers, timeout=4)
                if r.status_code == 400:
                    pp('Your Client-ID is not identified, your API calls will fail', mtype='ERROR')
                    return False
                if r.status_code != 200:
                    pp("Client-ID wasn't checked, trying again", mtype='WARNING')
                    cnt += 1
                    continue
                if r.json()['identified']:
                    pp('Your Client-ID is ok, you can use API calls')
                    return True
                else:
                    pp('Your Client-ID is not identified, your API calls will fail', mtype='ERROR')
                    return False
            except KeyError:
                pp("There is no 'identified' key, Client-ID wasn't checked, trying again", mtype='WARNING')
                cnt += 1
            except (requests.RequestException, ValueError):
                pp("Client-ID wasn't checked, trying again", mtype='WARNING')
                cnt += 1
        pp("Unable to check Client-ID in {} retries".format(retries), mtype='WARNING')
        return False

    def check_for_sub(self, msg):
        res = self.resub_pat.search(msg) or self.sub_pat.search(msg)
        if res:
            res = list(res.groups())
        else:
            return tuple()
        res[2] = res[2] == 'Twitch Prime'  # this is either "Twitch Prime" or "a #<amount> sub"
        # in case of new sub, month = 0
        return (res[0], res[1].replace('\s', ''), 0, res[2]) if len(res) == 3 else (res[3], res[1], int(res[0]), res[2])

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
        if not self.config['oauth_password'].startswith('oauth:'):
            pp("OAuth password should start with 'oauth:'", mtype='error')

        self.irc.get_irc_socket_object()
        self.load_or_create_channel_list()
        self.load_command_funcs()

        self.clientid_identified = self.check_client_id()

        trd = threading.Thread(target=self.check_channel_state, args=())
        trd.start()

        say_cd = '/w (sender) Команда будет доступна через {} сек'
        pbot_on_cd = 'Command is on cooldown. ({}) ({}) ({}s remaining)'
        pbot_not_on_cd = 'Command is valid and not on cooldown. ({}) ({})'

        while True:
            #time.sleep(0.003)
            try:
                data = self.irc.recv(self.config['socket_buffer_size']).decode().rstrip()
            except Exception:
                data = 'empty'

            if len(data) == 0:
                pp('Connection was lost, reconnecting.')
                self.irc.get_irc_socket_object()

            if time.time() - self.cmd_headers['!ragnaros']['time'] >= 7.0:
                self.cmd_headers['!ragnaros']['time'] = time.time()
                for ch in self.config['channels']:
                    for r in self.call_func('!ragnaros', ['check'], Message('', '', '', ch)):
                        self.send_to_chat(r, channel=ch)

            if time.time() - self.cmd_headers['!duel']['time'] >= 5.0:
                for ch in self.config['channels']:
                    for duel_resp in self.call_func('!duel', ['chk'], Message('', '', '', ch)):
                        self.send_to_chat(duel_resp, channel=ch)
                self.cmd_headers['!duel']['time'] = time.time()

            for data_line in data.split('\r\n'):
                if self.config['debug'] and data_line != 'empty':
                    print(data_line)

                self.irc.check_for_ping(data_line)
                self.sub_greetings(self.check_for_sub(data_line))

                if self.check_for_message(data_line):
                    msg = Message(**self.parse_message(data_line))

                    ##### RANDOM CUSTOM STUFF

                    ##### END OF RANDOM CUSTOM STUFF

                    if not self.config['debug']:
                        ppi(msg.chan, msg.message, msg.disp_name)

                    self.chat_messages[msg.chan].appendleft(msg)

                    if self.cmd_headers.is_valid_command(msg.message.split(' ')[0]):
                        command = msg.message
                        command_name = self.cmd_headers.get_real_name(command.split(' ')[0])

                        if self.cmd_headers.returns_command(command_name):
                            if self.cmd_headers.has_correct_args(command, command_name):
                                args = command.split(' ')
                                del args[0]

                                if self.cmd_headers.is_on_cooldown(command_name, msg.chan):
                                    sec_remaining = self.cmd_headers.get_cooldown_remaining(command_name, msg.chan)
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
                                        self.cmd_headers.update_last_used(command_name, msg.chan, msg.name)
                            else:
                                pp("Invalid number of arguments for '{}'".format(command_name))

                        else:
                            if self.cmd_headers.is_on_cooldown(command_name, msg.chan):
                                sec_remaining = self.cmd_headers.get_cooldown_remaining(command_name, msg.chan)
                                self.send_to_chat(say_cd.format(sec_remaining), msg.disp_name, msg.chan)
                                pbot(pbot_on_cd.format(command_name, msg.disp_name, sec_remaining), msg.chan)
                            else:
                                pbot(pbot_not_on_cd.format(command_name, msg.disp_name), msg.chan)
                                resp = self.cmd_headers.get_return(command_name)
                                self.cmd_headers.update_last_used(command_name, msg.chan, msg.name)
                                self.send_to_chat(resp, msg.disp_name, msg.chan)
