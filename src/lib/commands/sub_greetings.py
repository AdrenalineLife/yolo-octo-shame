# -*- coding: utf-8 -*-
__author__ = 'Life'


from src.res.sub_greetings_phrases import greetings
from src.lib.functions_general import pp

for x in greetings:
    if 'emote' not in greetings[x]:
        greetings[x]['emote'] = ''


def sub_greetings(self, args, msg):
    chan, name, month, is_prime = args
    try:
        if not is_prime:
            resp = greetings[chan]['resub'] if month else greetings[chan]['new']
        else:
            resp = greetings[chan]['resub_p'] if month else greetings[chan]['new_p']
        emote = greetings[chan]['emote'].strip() + ' '
        resp_kwargs = {
            'm': month,
            'name': name,
            'e': emote * month
        }
    except KeyError as e:
        pp('No key found: {} (sub_greetings.py)'.format(e), mtype='ERROR')
        return ''
    return resp.format(**resp_kwargs)
