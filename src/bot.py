# -*- coding: utf-8 -*-
"""
Simple IRC Bot for Twitch.tv
Developed by Aidan Thomson <aidraj0@gmail.com>
"""

import re
import src.lib.irc as irc_
import src.lib.functions_commands as f_commands
from src.lib.functions_general import *
from src.res.Message_class import Message


class Roboraj(object):
    def __init__(self, config):
        self.config = config
        self.irc = irc_.Irc(config)
        self.msg_pat = re.compile(r'@badges=.*;color=(.*);display-name=([a-zA-Z0-9_\\]*);emotes=.*;id=([a-zA-Z0-9-]*);mod=([01]);room-id=.*subscriber=([01]);.*turbo=([01]);user-id=.* :([a-zA-Z0-9_\\]*)!.*@.*tmi\.twitch\.tv PRIVMSG (#[a-zA-Z0-9_\\]+) :(.*)')

    def parse_message(self, msg):
        try:
            r = self.msg_pat.findall(msg)[0]
        except IndexError:
            print('>'*10, '\n', msg)
        # order: name, disp_name, msg, chan, color, is_sub, is_mod, is_turbo, id
        return r[6], r[1], r[8], r[7], r[0], r[4], r[3], r[5], r[2]

    def send_to_chat(self, result, username='', channel=''):
        resp = result.replace('(sender)', username)
        channel = '#jtv' if result.startswith('/w ') else channel
        pbot(resp, channel)
        self.irc.send_message(resp, channel)

    def check_for_sub(self, msg):
        # TODO test this
        exp1 = r'^@badges=.+emotes=.*;login=([a-zA-Z0-9_\\]+);.*;msg-id=resub;msg-param-months=([0-9]+);.+ :tmi\.twitch\.tv USERNOTICE (#[a-zA-Z0-9_\\]+).*'
        exp2 = r':twitchnotify!twitchnotify@twitchnotify[.]tmi[.]twitch[.]tv PRIVMSG (#[a-zA-Z0-9_]+) :([a-zA-Z0-9_\\]+) just subscribed!'
        res = re.findall(exp1, msg) or re.findall(exp2, msg)
        if res:
            res = res[0]
        else:
            return tuple()
        return (res[0], res[1], 0) if len(res) == 2 else (res[2], res[0], res[1])


    def run(self):
        config = self.config
        self.irc.get_irc_socket_object()

        say_cd = '/w (sender) Команда будет доступна через {} сек'
        pbot_on_cd = 'Command is on cooldown. ({}) ({}) ({}s remaining)'
        pbot_not_on_cd = 'Command is valid and not on cooldown. ({}) ({})'

        while True:
            time.sleep(0.005)
            try:
                data = self.irc.recv(config['socket_buffer_size']).decode().rstrip()
            except Exception:
                data = 'empty'

            if time.time() - f_commands.commands['!ragnaros']['time'] >= 7:
                f_commands.commands['!ragnaros']['time'] = time.time()
                for ch in config['channels']:
                    ragn_resp = f_commands.commands['!ragnaros']['function'](['check'], Message('', '', '', ch))
                    for r in ragn_resp:
                        self.send_to_chat(r, channel=ch)

            if time.time() - f_commands.commands['!duel']['time'] >= 5:
                for ch in config['channels']:
                    for duel_resp in f_commands.commands['!duel']['function'](['chk'], Message('', '', '', ch)):
                        self.send_to_chat(duel_resp, channel=ch)
                f_commands.commands['!duel']['time'] = time.time()

            for data_line in data.split('\r\n'):
                if len(data_line) == 0:
                    pp('Connection was lost, reconnecting.')
                    self.irc.get_irc_socket_object()

                if config['debug'] and data_line != 'empty':
                    print(data_line)

                self.irc.check_for_ping(data_line)

                if self.irc.check_for_message(data_line):
                    msg = Message(*self.parse_message(data_line))

                    if not config['debug']:
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
                                    self.send_to_chat(say_cd.format(sec_remaining), msg.disp_name, msg.chan)
                                    pbot(pbot_on_cd.format(command_name, msg.disp_name, sec_remaining), msg.chan)
                                else:
                                    pbot(pbot_not_on_cd.format(command_name, msg.disp_name), msg.chan)

                                    result = f_commands.pass_to_function(command_name, args, msg)
                                    f_commands.update_last_used(command_name, msg.chan)

                                    if result:
                                        if type(result) == list:
                                            for r in result:
                                                self.send_to_chat(r, msg.disp_name, msg.chan)
                                        else:
                                            self.send_to_chat(result, msg.disp_name, msg.chan)
                            else:
                                pp("Invalid number of arguments for '{}'".format(command_name))

                        else:
                            if f_commands.is_on_cooldown(command_name, msg.chan):
                                sec_remaining = f_commands.get_cooldown_remaining(command_name, msg.chan)
                                self.send_to_chat(say_cd.format(sec_remaining), msg.disp_name, msg.chan)
                                pbot(pbot_on_cd.format(command_name, msg.disp_name, sec_remaining), msg.chan)
                            elif f_commands.check_has_return(command_name):
                                pbot(pbot_not_on_cd.format(command_name, msg.disp_name), msg.chan)
                                resp = f_commands.get_return(command_name)
                                f_commands.update_last_used(command_name, msg.chan)
                                self.send_to_chat(resp, msg.disp_name, msg.chan)
