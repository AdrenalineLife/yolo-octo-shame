# -*- coding: utf-8 -*-

from random import randint

turned_on = {
    '#c_a_k_e': False,
    '#nastjanastja': False,
    '#adrenaline_life': False,
    '#a_o_w': False
}

allowed_users = ('a_o_w', 'adrenaline_life', 'c_a_k_e', 'nastjanastja')


def lavki(args, chan, username):
    if len(args) == 1 and args[0] in ('on', 'off'):
        if username in allowed_users:
            turned_on[chan] = True if args[0] == 'on' else False
        return ''

    if turned_on[chan] or username in allowed_users:
        check_string = ' '.join(args)
        return 'ты лавки {0} на {1}%'.format(check_string, randint(0, 100))
