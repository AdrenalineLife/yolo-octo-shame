# -*- coding: utf-8 -*-
__author__ = 'Life'

'''
This is a dict containing phrases to greet subscribers
The forming of a response happens in src/lib/commands/sub_greetings.py
Chan name is lowcase and starts with "#". For each channel:
    'new' - string for new non-prime sub
    'resub' - for resubscription
    'new_p' - for new prime sub
    'resub_p' - for prime resubscription
    'emote' - emote that is used in {e}
Python built-in string formatting is used, where:
    {name} - username of a subscriber
    {m} - number of months; in case of new sub month = 0
    {e} - 'm' times of 'emote'
'''

greetings = {
    '#channel1': {
        'new': 'Thanks for sub, {name}',
        'resub': 'ty for {m} month, {name}!',
        'new_p': 'Thank you for Prime!',
        'resub_p': 'thanks for resubbing for {m} month with twitch prime, {name}',
        'emote': 'Kappa'
    },
    '#channel2': {
        'new': '',
        'resub': '',
        'new_p': '',
        'resub_p': '',
        'emote': 'Keepo'
    },
    '#channel3': {
        'new': '',
        'resub': '',
        'new_p': '',
        'resub_p': '',
        'emote': 'Keepo'
    }
}
