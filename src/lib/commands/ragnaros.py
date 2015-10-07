# -*- coding: utf-8 -*-
__author__ = 'Life'

import time
import random


get_in_trap_time = 30
ban_time = 2*60
victims = dict()

allowed = ('c_a_k_e', 'a_o_w', 'nastjanastja')


def ragnaros(args, chan, username):
    if chan == '#c_a_k_e':
        if args and args[0] == 'check':
            remove = [x for x in victims if time.time() - victims[x] >= get_in_trap_time]
            for x in remove:
                victims.pop(x, None)

            #print(json.dumps(victims, indent=4))
            return ''

        if args and args[0] == 'add':
            if args[1] not in allowed:
                victims[args[1]] = time.time()
            return ''

        if username in allowed:
            if victims:
                vic = random.choice(list(victims.keys()))
                return [
                    '/timeout {0} {1}'.format(vic, ban_time),
                    '{0}, Рагнарос попал в тебя!'.format(vic)
                ]
            else:
                return ''
        else:
            return ''
