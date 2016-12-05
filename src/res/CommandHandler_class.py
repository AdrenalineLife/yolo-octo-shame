__author__ = 'Life'

import time


class CommandHandler(dict):
    def __init__(self, x):
        super().__init__(x)

    def is_valid_command(self, command):
        return command in self

    def has_correct_args(self, message, command):
        qty = len(message.split(' ')) - 1
        return self[command]['argc_min'] <= qty <= self[command]['argc_max']

    def is_on_cooldown(self, command, channel):
        return time.time() - self[command][channel]['last_used'] < self[command]['limit']

    def get_cooldown_remaining(self, command, channel):
        return round(self[command]['limit'] - (time.time() - self[command][channel]['last_used']))

    def update_last_used(self, command, channel, name):
        self[command][channel]['last_used'] = time.time()
        self[command][channel]['last_used_name'] = name

    def returns_command(self, name):
        return self[name]['return'] == 'command'

    def get_return(self, name):
        return self[name]['return']

if __name__ == '__main__':
    d = {'1':2, '2':3, '3':4}
    ch = CommandHandler(d)
    for a in ch:
        print(a)
    pass