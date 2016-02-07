# -*- coding: utf-8 -*-
"""
Simple IRC Bot for Twitch.tv
Developed by Aidan Thomson <aidraj0@gmail.com>
"""

import time

import src.lib.irc as irc_
from src.lib.functions_general import *
import src.lib.functions_commands as f_commands


class Roboraj:
    def __init__(self, config):
        self.config = config
        self.irc = irc_.irc(config)
        self.socket = self.irc.get_irc_socket_object()

        self.irc_w = irc_.irc(config, True)
        self.socket_w = self.irc_w.get_irc_socket_object()

    @staticmethod
    def is_whisper(msg):
        return msg.startswith('/w')

    def send_to_chat(self, result, username, channel):
        resp = result.replace('(sender)', username)
        pbot(resp, channel)
        if self.is_whisper(resp):
            self.irc_w.send_whisper(resp)
        else:
            self.irc.send_message(channel, resp)

    def run(self):
        sock = self.socket

        sock_w = self.socket_w
        config = self.config

        say_cd = '{0} Команда будет доступна через {1} сек'

        while True:
            try:
                data = sock.recv(config['socket_buffer_size']).decode().rstrip()
            except Exception:
                data = 'empty'

            try:
                data_w = sock_w.recv(config['socket_buffer_size']).decode().rstrip()
            except Exception:
                data_w = 'empty'

            self.irc_w.check_for_ping(data_w)

            if time.time() - f_commands.commands['!ragnaros']['time'] >= 7:
                f_commands.commands['!ragnaros']['time'] = time.time()
                for ch in config['channels']:
                    ragn_resp = f_commands.commands['!ragnaros']['function'](['check'], ch, '')
                    if ragn_resp:
                        for r in ragn_resp:
                            self.irc.send_message('#c_a_k_e', r)
                            pbot(r, '#c_a_k_e')

            if time.time() - f_commands.commands['!duel']['time'] >= 5:
                for ch in config['channels']:
                    for duel_resp in f_commands.commands['!duel']['function'](['chk'], ch, ''):
                        self.irc.send_message(ch, duel_resp)
                f_commands.commands['!duel']['time'] = time.time()

            data_list = data.split('\r\n')

            for data_line in data_list:
                if len(data_line) == 0:
                    pp('Connection was lost, reconnecting.')
                    sock = self.irc.get_irc_socket_object()

                if config['debug']:
                    print(data_line)

                # check for ping, reply with pong
                self.irc.check_for_ping(data_line)

                if self.irc.check_for_message(data_line):
                    try:
                        message_dict = self.irc.get_message(data_line)
                    except UnicodeEncodeError as detail:
                        pp('UnicodeEncodeError: %s' % detail, 'error')
                    except UnicodeDecodeError as detail:
                        pp('UnicodeDecodeError: %s' % detail, 'error')

                    channel = message_dict['channel']
                    message = message_dict['message']
                    username = message_dict['username']

                    ppi(channel, message, username)

                    #a = time.time()
                    f_commands.commands['!ragnaros']['function'](['add', username], channel, '')
                    #print(time.time() - a)

                    # check if message is a command with no arguments.
                    if f_commands.is_valid_command(message) or f_commands.is_valid_command(message.split(' ')[0]):
                        command = message
                        command_name = command.split(' ')[0]

                        if f_commands.check_returns_function(command_name):
                            if f_commands.check_has_correct_args(command, command_name):
                                args = command.split(' ')
                                del args[0]

                                if f_commands.is_on_cooldown(command_name, channel):
                                    sec_remaining = f_commands.get_cooldown_remaining(command_name, channel)
                                    self.irc_w.send_whisper(say_cd.format(username, sec_remaining))
                                    pbot('Command is on cooldown. (%s) (%s) (%ss remaining)' % (
                                        command_name, username, sec_remaining),
                                        channel
                                        )
                                else:
                                    pbot('Command is valid an not on cooldown. (%s) (%s)' % (
                                        command_name, username),
                                        channel
                                        )

                                    result = f_commands.pass_to_function(command_name, args, channel, username)
                                    f_commands.update_last_used(command_name, channel)

                                    if result:
                                        if type(result) == list:
                                            for r in result:
                                                self.send_to_chat(r, username, channel)
                                        else:
                                            self.send_to_chat(result, username, channel)

                        else:
                            if f_commands.is_on_cooldown(command_name, channel):
                                sec_remaining = f_commands.get_cooldown_remaining(command_name, channel)
                                self.irc_w.send_whisper(say_cd.format(username, sec_remaining))
                                pbot('Command is on cooldown. (%s) (%s) (%ss remaining)' % (
                                    command_name, username, sec_remaining),
                                    channel
                                    )
                            elif f_commands.check_has_return(command_name):
                                pbot('Command is valid and not on cooldown. (%s) (%s)' % (
                                    command_name, username),
                                    channel
                                    )
                                f_commands.update_last_used(command_name, channel)

                                resp = f_commands.get_return(command_name).replace('(sender)', username)
                                f_commands.update_last_used(command_name, channel)

                                pbot(resp, channel)
                                self.irc.send_message(channel, resp)
