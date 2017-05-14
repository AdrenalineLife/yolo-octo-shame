# -*- coding: utf-8 -*-
__author__ = 'Life'


from src.res.uncover_names import uncover

'''Command to display multistream link.
you can use your shortened versions of nicks.
place '*' before nick if you dont want it to be uncovered'''

ALLOWED_USERS = (75386043,
                 )
LINK = 'https://multistre.am/{}/{}/layout3/'
cache = {}


def ms(self, args, msg):
    if args:
        if msg.is_mod or msg.user_id in ALLOWED_USERS:
            chan_name = msg.chan.lstrip('#')  # current chan name
            args_ = (x.lstrip('@').lower() for x in args)
            chans = [x.strip('*') for x in (uncover.get(i, i) for i in args_)
                     if x != chan_name]
            resp = LINK.format(chan_name, '/'.join(chans))
            cache[msg.chan_id] = resp
            return resp
    else:
        return cache.get(msg.chan_id, '')
