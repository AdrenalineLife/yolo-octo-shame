# -*- coding: utf-8 -*-

import importlib
from src.config.config import *
from src.lib.functions_general import pp

commands = {
    '!test': {
        'limit': 0,
        'return': '.me This is a test!'
    },

    '!randomemote': {
        'limit': 0,
        'argc_min': 0,
        'argc_max': 0,
        'return': 'command'
    },

    '!vksong': {
        'limit': 0,
        'argc_min': 0,
        'argc_max': 0,
        'return': 'command'
    },

    '!prime': {
        'limit': 0,
        'argc_min': 1,
        'argc_max': 1,
        'return': 'command'
    },

    '!lavki': {
        'limit': 0,
        'argc_min': 1,
        'argc_max': 10,
        'return': 'command'
    },

    '!pyramid': {
        'limit': 0,
        'argc_min': 1,
        'argc_max': 2,
        'return': 'command'
    },

    '!duel': {
        'limit': 0,
        'argc_min': 0,
        'argc_max': 2,
        'return': 'command',
    },

    '!history': {
        'limit': 0,
        'argc_min': 0,
        'argc_max': 1,
        'return': 'command'
    },

    '!dubsong': {
        'limit': 0,
        'argc_min': 0,
        'argc_max': 0,
        'return': 'command'
    },

    '!m8': {
        'limit': 0,
        'argc_min': 0,
        'argc_max': 0,
        'return': 'command'
    },

    '!ragnaros': {
        'limit': 0,
        'argc_min': 0,
        'argc_max': 1,
        'return': 'command',
        'ch_time': 4,
    }
}

for channel in config['channels']:
    for command in commands:
        commands[command]['time'] = 0
        commands[command][channel] = {}
        commands[command][channel]['last_used'] = 0

missing_func = []

for command in commands:
    if commands[command]['return'] == 'command':
        try:
            module = importlib.import_module('src.lib.commands.%s' % command[1:])
            commands[command]['function'] = getattr(module, command[1:])
        except ImportError:
            missing_func.append(command)
            pp('No module found: %s' % command, 'error')
        except AttributeError:
            missing_func.append(command)
            pp('No function found: %s' % command, 'error')

# deleting commands from dict which we did not find
for f in missing_func:
    commands.pop(f, None)