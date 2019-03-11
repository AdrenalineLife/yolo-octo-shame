# -*- coding: utf-8 -*-
"""
Simple IRC Bot for Twitch.tv
Developed by Aidan Thomson <aidraj0@gmail.com>
"""

import importlib
import threading
import requests
import traceback
import json
import os.path
from collections import deque, Iterable

import src.lib.irc as irc_
import src.lib.command_headers as c_headers

from src.lib.functions_general import *
from src.res.Message_class import Message
from src.res.Channel_class import Channel
from src.res.CommandHandler_class import CommandHandler


SAY_CD = '/w (sender) Команда будет доступна через {} сек'
PBOT_ON_CD = 'Command is on cooldown. ({}) ({}) ({}s remaining)'
PBOT_NOT_ON_CD = 'Command is valid and not on cooldown. ({}) ({})'
PBOT_INVALID_ARGUMENTS = "Invalid number of arguments for '{}'"
DATA_EMPTY = '<empty>'  # a constant used when socket has nothing to receive


class Roboraj(object):
    def __init__(self, config, config_misc):
        self.config = config
        self.config_misc = config_misc
        self.irc = irc_.IRC(config, config_misc)

        # list of channels
        self.ch_list = list()

        # info about commands
        self.cmd_headers = CommandHandler(c_headers.commands)

        # stores <maxlen> last messages of chat
        self.chat_messages = {chan: deque(maxlen=self.config_misc['chat_messages_maxlen'])
                              for chan in self.config['channels']}

        # headers for all API requests
        self.req_headers = {'Client-ID': self.config['Client-ID'],
                            'authorization': self.config['api_token'],
                            'Accept': self.config['api_version']}

        # boolean to indicate if Client-ID is identified
        self.clientid_identified = False

        # session for API requests to get streams info
        self.chans_request = requests.Session()
        self.chans_request.headers = self.req_headers

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
            for x in self.ch_list:
                x.init_on_load()

            # adding missing channels
            loaded_ch = [x.name for x in self.ch_list]
            for x in self.config['channels']:
                if x.lstrip('#') not in loaded_ch:
                    self.ch_list.append(Channel(x.lstrip('#'), self.req_headers))

    def load_command_funcs(self):
        missing_func = []
        missing_module = []
        whiteblacklist = []
        for cmd_name, command in self.cmd_headers.items():
            if 'ref' not in command:
                # load corresponding function if it returns command
                if command['return'] == 'command':
                    try:
                        module_ = importlib.import_module('src.lib.commands.' + cmd_name[1:])
                        setattr(self.__class__, cmd_name, getattr(module_, cmd_name[1:]))
                    except ImportError:
                        missing_module.append(cmd_name)
                    except AttributeError:
                        missing_func.append(cmd_name)

                # commands that don't have a 'return'
                if 'return' not in command or not command['return']:
                    pp("{} command does not have 'return'".format(cmd_name), mtype='WARNING')
                    missing_func.append(cmd_name)

                # commands that have both whitelists and blacklists
                if 'whitelist' in command and 'blacklist' in command:
                    whiteblacklist.append(cmd_name)

        if missing_module:
            pp('No module found: {}'.format(', '.join(missing_module)), mtype='WARNING')
        if missing_func:
            pp('No function found: {}'.format(', '.join(missing_func)), mtype='WARNING')
        # deleting commands from dict which we did not find
        for f in missing_func + missing_module:
            self.cmd_headers.pop(f, None)

        if whiteblacklist:
            pp('Commands {} have both "whitelist" and "blacklist". Note that blacklist has priority'.format(
                ', '.join(whiteblacklist)), mtype='warning')

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
        try:
            return getattr(self, command)(args, msg)
        except Exception as e:
            pp('Exception while calling function "{}". {}: {}'.format(
                command, e.__class__.__name__, e), mtype='error')

            report = '{time} {cmd} {msg}\r\n\r\n{tb}{sep}\r\n'
            with open(os.path.join('input_output', 'func_exceptions.txt'), 'at', encoding='utf8') as f_:
                f_.write(report.format(time=time.strftime('%d.%m.%y %H:%M:%S', time.localtime()),
                                       cmd=command,
                                       msg=msg,
                                       tb=traceback.format_exc(),
                                       sep='=' * 35))

    # get command response, whether it is a function or just a string
    def get_command_response(self, command, args, msg):
        if self.cmd_headers.returns_command(command):
            return self.call_func(command, args, msg)
        else:
            return self.cmd_headers.get_return(command)

    def get_ids_by_names(self):
        try:
            resp = self.chans_request.get('https://api.twitch.tv/kraken/users',
                                          timeout=7.0,
                                          params={'login': ','.join(x[1:] for x in self.config['channels'])})
            resp_j = resp.json()['users']
            if resp.status_code != 200:
                pp("Failed getting users ids, code {}".format(resp.status_code), mtype='ERROR')
                return

        except (requests.RequestException, ValueError, KeyError) as e:
            pp("Failed getting users ids, {}: {}".format(e.__class__.__name__, str(e)), mtype='ERROR')
            return
        # print('>>', json.dumps(resp_j, indent=4))

        not_found = []
        for ch in self.ch_list:
            try:
                chan_id = next((x['_id'] for x in resp_j if x['name'] == ch.name), '')
                ch.chan_id = chan_id
                if not chan_id:
                    not_found.append(ch.name)
            except KeyError as e:
                pp('Failed getting users ids, {} key is missing'.format(str(e)), mtype='error')
                continue
        if not_found:
            pp('Users not found: {}'.format(', '.join(not_found)), mtype='WARNING')
        pp('Got IDs by channel names')

    def check_channel_state(self):
        while True:
            try:
                # print(', '.join(str(time.time() - x._last_time_updated) for x in self.ch_list))
                resp = self.chans_request.get('https://api.twitch.tv/kraken/streams',
                                              timeout=5.0,
                                              params={'channel': ','.join(x.chan_id for x in self.ch_list)})
                resp_j = resp.json()
                #', '.join(str((x['channel']['name'], x['viewers'])) for x in resp_j['streams'])
                if resp.status_code != 200:
                    pp("Failed getting channels state, code {}".format(resp.status_code), mtype='ERROR')
                    time.sleep(6.0)
                    continue

            except (requests.RequestException, ValueError) as e:
                pp("Failed getting channels state, {}: {}".format(e.__class__.__name__, str(e)), mtype='ERROR')
                time.sleep(4.0)
                continue
            except KeyError as e:
                pp("There is no {} key in API response".format(str(e)), mtype='ERROR')
                time.sleep(4.0)
                continue
            # print('>>', json.dumps(resp_j, indent=4))

            for ch in self.ch_list:
                chan_info = next((x for x in resp_j['streams'] if x['channel']['name'] == ch.name), None)
                try:
                    ch.set_info(chan_info)
                except KeyError as e:
                    pp('Failed getting channel state, {} key is missing'.format(str(e)), mtype='error')
                    pp(json.dumps(resp_j, indent=4), mtype='error')
                    continue
                ch.check_state()

            save_obj(self.ch_list, 'channel_list')
            time.sleep(31.0)

    def is_whisper(self, response) -> bool:
        is_w = lambda x: x.startswith('/w ') or x.startswith('.w ') or \
               x.startswith('/W ') or x.startswith('.W ')
        if not isinstance(response, str) and isinstance(response, Iterable):
            return all(is_w(m) for m in response)
        return is_w(response)

    def send_to_chat(self, result, username='', channel='') -> bool:
        if not result:
            return False
        resp = result.replace('(sender)', username)
        channel = '#jtv' if self.is_whisper(result) else channel
        if self.irc.send_message(resp, channel):
            pbot(resp, channel)
            return True
        return False

    def send_messages(self, result, username='', channel='') -> bool:
        if result is None:
            return False
        result = (result,) if type(result) == str else result
        if type(result) in (list, tuple, set, deque):
            sent = [self.send_to_chat(r, username, channel) for r in result]  # list of bool
            return any(sent)  # True if at least one message was sent
        else:
            pp("Type {} is not allowed to be sent in chat".format(type(result)), mtype='error')
            return False

    def join_channels(self, channels):
        pass  # TODO

    # check if client id is identified
    def check_client_id(self, retries=3):
        cnt = 1
        while cnt <= retries:
            try:
                r = requests.get('https://api.twitch.tv/kraken/', headers=self.req_headers, timeout=4)
                # print('{} {} {}'.format(r.status_code, json.dumps(r.json(), indent=4), ''))
                if r.status_code == 400:
                    pp('Your Client-ID is not identified, your API calls will fail', mtype='ERROR')
                    return False
                if r.status_code != 200:
                    pp("Client-ID wasn't checked, trying again (code {})".format(r.status_code), mtype='WARNING')
                    cnt += 1
                    continue
                else:
                    pp('Your Client-ID is ok, you can use API calls')
                    return True
            except requests.RequestException:
                pp("Client-ID wasn't checked, trying again", mtype='WARNING')
                cnt += 1
        pp("Unable to check Client-ID in {} retries".format(retries), mtype='WARNING')
        return False

    def sub_greetings(self, sub_info):
        if not sub_info:
            return None
        resp = self.call_func('!sub_greetings', sub_info, None)
        self.send_messages(resp, channel=sub_info['chan'])
        self.cmd_headers['!sub_greetings']['time'] = time.time()

    def run(self):
        if not self.config['oauth_password'].startswith('oauth:'):
            pp("OAuth password should start with 'oauth:'", mtype='error')

        self.irc.init_irc_socket_object()
        self.load_or_create_channel_list()
        self.load_command_funcs()

        # self.clientid_identified = self.check_client_id()
        self.get_ids_by_names()

        trd = threading.Thread(target=self.check_channel_state, args=())
        trd.start()

        while True:
            time.sleep(0.003)
            try:
                data = self.irc.recv(self.config['socket_buffer_size']).decode().rstrip()
            except BlockingIOError:
                data = DATA_EMPTY

            if len(data) == 0:
                pp('Connection was lost, reconnecting')
                self.irc.init_irc_socket_object()

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
                if self.config_misc['debug'] and data_line != DATA_EMPTY:
                    print(data_line)

                self.irc.check_for_ping(data_line)
                if self.irc.is_usernotice.match(data_line):
                    '''
                    try:
                        uno = self.irc.parse_usernotice(data_line)
                    except Exception:
                        uno = data_line
                    f_ = open('userno.txt', 'at', encoding='utf8')
                    f_.write(str(uno))
                    f_.write('\r\n\r\n')
                    f_.close()'''
                    usernotice = self.irc.parse_usernotice(data_line)
                    #print(usernotice)
                    if self.irc.check_for_sub(usernotice):
                        self.sub_greetings(usernotice)

                if self.irc.check_for_message(data_line):
                    msg = Message(**self.irc.parse_message(data_line))

                    if self.config_misc['print_chat_msgs'] and not self.config_misc['debug']:
                        ppi(msg.chan, msg.message, msg.disp_name)

                    self.chat_messages[msg.chan].appendleft(msg)
                    if msg.name == self.config['username'].lower():  # if it is our own message
                        self.irc.msg_timestamps.append(time.time())

                    #continue

                    if self.cmd_headers.is_valid_command(msg.message.split(' ')[0], msg):
                        command_name = self.cmd_headers.get_real_name(msg.message.split(' ')[0])
                        args = msg.message.split(' ')
                        del args[0]

                        if self.cmd_headers.has_correct_args(args, command_name):
                            if self.cmd_headers.is_on_cooldown(command_name, msg):
                                sec_remaining = self.cmd_headers.get_cooldown_remaining(command_name, msg)
                                pbot(PBOT_ON_CD.format(command_name, msg.disp_name, sec_remaining), msg.chan)
                                if self.cmd_headers.need_to_notify_cd(command_name, msg):
                                    self.send_to_chat(SAY_CD.format(sec_remaining), msg.disp_name, msg.chan)
                            else:
                                pbot(PBOT_NOT_ON_CD.format(command_name, msg.disp_name), msg.chan)
                                result = self.get_command_response(command_name, args, msg)

                                was_sent = self.send_messages(result, msg.disp_name, msg.chan)
                                if was_sent:
                                    self.cmd_headers.update_last_used(
                                        command_name, msg, self.is_whisper(result))
                        else:
                            pp(PBOT_INVALID_ARGUMENTS.format(command_name))
