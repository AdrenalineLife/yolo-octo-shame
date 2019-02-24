# -*- coding: utf-8 -*-
__author__ = 'Life'

import time
import json


class CommandHandler(dict):
    def __init__(self, x):
        super().__init__(x)

    def is_valid_command(self, command):
        return command in self

    def has_correct_args(self, args, command):
        if not self.returns_command(command):
            return True
        qty = len(args)
        return self[command]['argc_min'] <= qty <= self[command]['argc_max']

    def is_on_cooldown(self, command, channel):
        return time.time() - self[command][channel]['last_used'] < self[command]['limit']

    def get_cooldown_remaining(self, command, channel):
        return round(self[command]['limit'] - (time.time() - self[command][channel]['last_used']))

    def update_last_used(self, command, channel, name, is_whisper):
        if self.need_to_update_last_used(command, is_whisper):
            self[command][channel]['last_used'] = time.time()
            self[command][channel]['last_used_name'] = name

    def need_to_update_last_used(self, command, is_whisper: bool):
        return not (is_whisper and self[command].get('whisper_no_cd', False))

    def returns_command(self, name):
        return self[name]['return'] == 'command'

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