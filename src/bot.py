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

    def run(self):
        irc = self.irc
        sock = self.socket
        config = self.config

        while True:
            try:
                data = sock.recv(config['socket_buffer_size']).decode().rstrip()
            except Exception:
                data = 'empty'

            if time.time() - f_commands.commands['!ragnaros']['time'] >= f_commands.commands['!ragnaros']['ch_time']:
                ragn_resp = f_commands.commands['!ragnaros']['function'](['check'], '#c_a_k_e', '')
                f_commands.commands['!ragnaros']['time'] = time.time()
                if ragn_resp:
                    for r in ragn_resp:
                        irc.send_message('#c_a_k_e', r)

            data_list = data.split('\r\n')

            for data_line in data_list:
                if len(data_line) == 0:
                    pp('Connection was lost, reconnecting.')
                    sock = self.irc.get_irc_socket_object()

                if config['debug']:
                    print(data_line)

                # check for ping, reply with pong
                irc.check_for_ping(data_line)

                if irc.check_for_message(data_line):
                    try:
                        message_dict = irc.get_message(data_line)
                    except UnicodeEncodeError as detail:
                        pp('UnicodeEncodeError: %s' % detail, 'error')
                    except UnicodeDecodeError as detail:
                        pp('UnicodeDecodeError: %s' % detail, 'error')

                    channel = message_dict['channel']
                    message = message_dict['message']
                    username = message_dict['username']

                    ppi(channel, message, username)

                    f_commands.commands['!ragnaros']['function'](['add', username], '#c_a_k_e', '')

                    # check if message is a command with no arguments.
                    if f_commands.is_valid_command(message) or f_commands.is_valid_command(message.split(' ')[0]):
                        command = message
                        command_name = command.split(' ')[0]

                        if f_commands.check_returns_function(command_name):
                            if f_commands.check_has_correct_args(command, command_name):
                                args = command.split(' ')
                                del args[0]

                                if f_commands.is_on_cooldown(command_name, channel):
                                    pbot('Command is on cooldown. (%s) (%s) (%ss remaining)' % (
                                        command_name, username,
                                        f_commands.get_cooldown_remaining(command_name, channel)),
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
                                                resp = r.replace('(sender)', username)
                                                pbot(resp, channel)
                                                irc.send_message(channel, resp)
                                        else:
                                            resp = result.replace('(sender)', username)
                                            pbot(resp, channel)
                                            irc.send_message(channel, resp)

                        else:
                            if f_commands.is_on_cooldown(command_name, channel):
                                pbot('Command is on cooldown. (%s) (%s) (%ss remaining)' % (
                                    command_name, username, f_commands.get_cooldown_remaining(command_name, channel)),
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
                                irc.send_message(channel, resp)
