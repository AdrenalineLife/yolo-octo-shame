from src.config.config import *
import importlib

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

    '!wow': {
        'limit': 30,
        'argc_min': 3,
        'argc_max': 3,
        'return': 'command'
    },

    '!vksong': {
        'limit': 0,
        'argc_min': 0,
        'argc_max': 0,
        'return': 'command'
    },

    '!plugsong': {
        'limit': 0,
        'argc_min': 0,
        'argc_max': 0,
        'return': 'command'
    },

    '!lavki': {
        'limit': 0,
        'argc_min': 1,
        'argc_max': 10,
        'return': 'command'
    }
}

for channel in config['channels']:
    for command in commands:
        commands[command][channel] = {}
        commands[command][channel]['last_used'] = 0
        commands[command][channel]['my_last_used'] = 0

for command in commands:
    if commands[command]['return'] == 'command':
        module = importlib.import_module('src.lib.commands.%s' % command[1:])
        commands[command]['function'] = getattr(module, command[1:])


#module = importlib.import_module('src.lib.commands.%s' % command)
#function = getattr(module, command)