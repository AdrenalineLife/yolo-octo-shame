# -*- coding: utf-8 -*-
__author__ = 'Life'

import time
import json
import random


class CommandHandler(dict):
    def __init__(self, x):
        super().__init__(x)

    def is_valid_command(self, command, msg):
        present = command in self
        if not present:
            return False
        black = self[command].get('blacklist', [])
        if black:
            return msg.chan not in black

        white = self[command].get('whitelist', [])
        if white:
            return msg.chan in white
        else:
            return True

    def has_correct_args(self, args, command):
        if not self.returns_command(command):
            return True
        qty = len(args)
        return self[command]['argc_min'] <= qty <= self[command]['argc_max']

    def is_on_cooldown(self, command, msg):
        if msg.is_mod and self[command].get('mods_ignore_cd', False):
            return False
        
        subs_ignore = self[command].get('subs_ignore_cd', None)
        if subs_ignore is not None:
            if msg.badges.get('subscriber', 0) >= subs_ignore:
                return False
        return time.time() - self[command][msg.chan]['last_used'] < self[command]['limit']

    def get_cooldown_remaining(self, command, msg):
        return round(self[command]['limit'] - (time.time() - self[command][msg.chan]['last_used']))

    def update_last_used(self, command, msg, is_whisper):
        if self.need_to_update_last_used(command, msg, is_whisper):
            self[command][msg.chan]['last_used'] = time.time()
            self[command][msg.chan]['last_used_name'] = msg.name

    def need_to_update_last_used(self, command, msg, is_whisper: bool):
        if msg.is_mod and self[command].get('mods_ignore_cd', False):
            return False
        if msg.badges.get('subscriber', 0) >= self[command].get('subs_ignore_cd', 0):
            return False
        return not (is_whisper and self[command].get('whisper_no_cd', False))

    def need_to_notify_cd(self, command, msg):
        if msg.is_mod or msg.badges.get('subscriber', 0) >= 3:
            return True
        return random.random() <= 0.35

    def returns_command(self, command):
        return self[command]['return'] == 'command'

    def get_return(self, command):
        return self[command]['return']

    def get_real_name(self, command):
        return self[command]['name']

    def is_reference(self, command):
        return self.get_real_name(command) != command

    def __repr__(self):
        return json.dumps(self.__dict__, indent=4)


if __name__ == '__main__':
    d = {'1':2, '2':3, '3':4}
    ch = CommandHandler(d)
    for a in ch:
        print(a)
    pass