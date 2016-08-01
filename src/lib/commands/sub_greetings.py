# -*- coding: utf-8 -*-
__author__ = 'Life'


greetings = {
    '#c_a_k_e': {
        'new': 'Приветствуем новобранца {n}!',
        'resub': 'Спасибо за подписку, {n}! {m} месяцев {e}',
        'emote': 'Kappa'
    },
    '#nastjanastja': {
        'new': 'Thank you, {n}!',
        'resub': 'Thanks {n} for {m} month! {e}',
        'emote': 'Keepo'
    },
    '#': {
        'new': '',
        'resub': ''
    }
}

def sub_greetings(self, args, msg):
    global greetings
    chan, name, month = args
    try:
        resp = greetings[chan]['resub'] if month else greetings[chan]['new']
        emote = greetings[chan]['emote'].strip() + ' '
        str_kwargs = {
            'm': month,
            'n': name,
            'e': (emote * month).rstrip()
        }
    except KeyError:
        return ''
    return resp.format(**str_kwargs)
