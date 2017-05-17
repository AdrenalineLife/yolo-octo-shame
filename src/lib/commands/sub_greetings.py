# -*- coding: utf-8 -*-
__author__ = 'Life'


from src.res.sub_greetings_phrases import greetings
from src.lib.functions_general import pp

for x in greetings:
    if 'emote' not in greetings[x]:
        greetings[x]['emote'] = ''


def sub_greetings(self, args, msg):
    chan, name, month, plan = args
    is_prime = plan.lower() == 'prime'
    chan_greets = greetings.get(chan, None)
    if chan_greets is None:  # TODO notify as an option
        return ''

    try:
        if not is_prime:
            resp = chan_greets['resub'] if month else chan_greets['new']
        else:
            resp = chan_greets['resub_p'] if month else chan_greets['new_p']
        emote = chan_greets['emote'].strip() + ' '
        resp_kwargs = {
            'm': month,
            'name': name,
            'e': emote * month
        }
    except KeyError as e:
        pp('No key found: {} (sub_greetings.py)'.format(e), mtype='ERROR')
        return ''
    return resp.format(**resp_kwargs)
