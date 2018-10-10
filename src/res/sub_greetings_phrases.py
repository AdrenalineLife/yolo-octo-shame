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
    'gift' - for gifts
    'gifted_total' - msg about total amount of gifts, later it concatenates with 'gift'
    'submysterygift' - for mystery gifts (random gifts)
Python built-in string formatting is used, where:
    {name} - username of a subscriber
    {m} - number of months; in case of new sub month = 0
    {e} - 'm' times of 'emote'
    {msg_param_sender_count} - total amount of gifts given by user
    {msg_param_mass_gift_count} - amount of subs gifted in a single mysterygift
'''

greetings = {
    '#c_a_k_e_': {
        'new': '{name}',
        'resub': '{name} {m}',
        'new_p': 'p {name}',
        'resub_p': 'p {name} {m}',
        'gift': '',
        'gifted_total': '{msg_param_sender_count}',
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
