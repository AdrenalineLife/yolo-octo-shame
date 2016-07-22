# -*- coding: utf-8 -*-

from random import randint

turned_on = {
    '#c_a_k_e': False,
    '#nastjanastja': False,
    '#adrenaline_life': False,
    '#a_o_w': True
}

allowed_users = ('a_o_w', 'adrenaline_life', 'c_a_k_e', 'nastjanastja')


def lavki(self, args, msg):
    if len(args) == 1 and args[0] in ('on', 'off'):
        if msg.name in allowed_users:
            turned_on[msg.chan] = True if args[0] == 'on' else False
        return ''

    if turned_on[msg.chan] or msg.name in allowed_users:
        check_string = ' '.join(args)
        return 'ты лавки {} на {}%'.format(check_string, randint(0, 100), msg.name)
