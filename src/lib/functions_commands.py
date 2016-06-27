import time

from src.config.config import *
from src.lib.command_headers import *


def is_valid_command(command):
    if command in commands:
        return True


def update_last_used(command, channel):
    commands[command][channel]['last_used'] = time.time()


def get_command_limit(command):
    return commands[command]['limit']


def is_on_cooldown(command, channel):
    if time.time() - commands[command][channel]['last_used'] < commands[command]['limit']:
        return True


def get_cooldown_remaining(command, channel):
    return round(commands[command]['limit'] - (time.time() - commands[command][channel]['last_used']))


def check_has_return(command):
    if commands[command]['return'] and commands[command]['return'] != 'command':
        return True


def get_return(command):
    return commands[command]['return']


def check_has_args(command):
    if 'argc' in commands[command]:
        return True


def check_has_correct_args(message, command):
    qty = len(message.split(' ')) - 1
    if commands[command]['argc_min'] <= qty <= commands[command]['argc_max']:
        return True


def check_returns_function(command):
    if commands[command]['return'] == 'command':
        return True


def pass_to_function(command, args, msg):
    return commands[command]['function'](args, msg)