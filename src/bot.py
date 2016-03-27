# -*- coding: utf-8 -*-
"""
Simple IRC Bot for Twitch.tv
Developed by Aidan Thomson <aidraj0@gmail.com>
"""

import src.lib.irc as irc_
from src.lib.functions_general import *
import src.lib.functions_commands as f_commands
from src.res.Message_class import Message


class Roboraj(object):
    def __init__(self, config):
        self.config = config
        self.irc = irc_.Irc(config)
        self.irc_w = irc_.Irc(config, True)

    @staticmethod
    def is_whisper(msg):
        return msg.startswith('/w ')

    def send_to_chat(self, result, username, channel):
        resp = result.replace('(sender)', username)
        pbot(resp, channel)
        if self.is_whisper(resp):
            self.irc_w.send_whisper(resp)
        else:
            self.irc.send_message(channel, resp)

    def run(self):
        config = self.config
        self.irc.get_irc_socket_object()
        self.irc_w.get_irc_socket_object()

        say_cd = '/w {0} Команда будет доступна через {1} сек'

        while True:
            try:
                data = self.irc.recv(config['socket_buffer_size']).decode().rstrip()
            except Exception:
                data = 'empty'

            try:
                data_w = self.irc_w.recv(config['socket_buffer_size']).decode().rstrip()
            except Exception:
                data_w = 'empty'

            self.irc_w.check_for_ping(data_w)

            if time.time() - f_commands.commands['!ragnaros']['time'] >= 7:
                f_commands.commands['!ragnaros']['time'] = time.time()
                for ch in config['channels']:
                    ragn_resp = f_commands.commands['!ragnaros']['function'](['check'], Message(None, True, '', '', ch))
                    for r in ragn_resp:
                        self.irc.send_message(ch, r)
                        pbot(r, ch)

            if time.time() - f_commands.commands['!duel']['time'] >= 5:
                for ch in config['channels']:
                    for duel_resp in f_commands.commands['!duel']['function'](['chk'], Message(None, True, '', '', ch)):
                        self.irc.send_message(ch, duel_resp)
                        pbot(duel_resp, ch)
                f_commands.commands['!duel']['time'] = time.time()

            data_list = data.split('\r\n')

            for data_line in data_list:
                if len(data_line) == 0:
                    pp('Connection was lost, reconnecting.')
                    sock = self.irc.get_irc_socket_object()

                if config['debug'] and data_line != 'empty':
                    print(data_line)

                # check for ping, reply with pong
                self.irc.check_for_ping(data_line)

                if self.irc.check_for_message(data_line):
                    msg = Message(data_line)
                    #print(msg)

                    ppi(msg.chan, msg.message, msg.disp_name)

                    f_commands.commands['!ragnaros']['function'](['add'], msg)

                    # check if message is a command with no arguments.
                    if f_commands.is_valid_command(msg.message) or f_commands.is_valid_command(msg.message.split(' ')[0]):
                        command = msg.message
                        command_name = command.split(' ')[0]

                        if f_commands.check_returns_function(command_name):
                            if f_commands.check_has_correct_args(command, command_name):
                                args = command.split(' ')
                                del args[0]

                                if f_commands.is_on_cooldown(command_name, msg.chan):
                                    sec_remaining = f_commands.get_cooldown_remaining(command_name, msg.chan)
                                    self.irc_w.send_whisper(say_cd.format(msg.name, sec_remaining))
                                    pbot('Command is on cooldown. (%s) (%s) (%ss remaining)' % (
                                        command_name, msg.name, sec_remaining),
                                        msg.chan
                                        )
                                else:
                                    pbot('Command is valid and not on cooldown. (%s) (%s)' % (
                                        command_name, msg.name),
                                        msg.chan
                                        )

                                    result = f_commands.pass_to_function(command_name, args, msg)
                                    f_commands.update_last_used(command_name, msg.chan)

                                    if result:
                                        if type(result) == list:
                                            for r in result:
                                                self.send_to_chat(r, msg.disp_name, msg.chan)
                                        else:
                                            self.send_to_chat(result, msg.name, msg.chan)
                            else:
                                pp('Invalid number of arguments for {}'.format(command_name))

                        else:
                            if f_commands.is_on_cooldown(command_name, msg.chan):
                                sec_remaining = f_commands.get_cooldown_remaining(command_name, msg.chan)
                                self.irc_w.send_whisper(say_cd.format(msg.name, sec_remaining))
                                pbot('Command is on cooldown. (%s) (%s) (%ss remaining)' % (
                                    command_name, msg.name, sec_remaining),
                                    msg.chan
                                    )
                            elif f_commands.check_has_return(command_name):
                                pbot('Command is valid and not on cooldown. (%s) (%s)' % (
                                    command_name, msg.name),
                                    msg.chan
                                    )
                                f_commands.update_last_used(command_name, msg.chan)

                                resp = f_commands.get_return(command_name).replace('(sender)', msg.disp_name)
                                f_commands.update_last_used(command_name, msg.chan)

                                pbot(resp, msg.chan)
                                self.irc.send_message(msg.chan, resp)
