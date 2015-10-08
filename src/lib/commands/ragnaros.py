# -*- coding: utf-8 -*-
__author__ = 'Life'

import time
import random
import json


color = 'Red'  # color for using me
hit_freq = 5*60  # ban every hit_freq seconds
last_time_hit = 0
get_in_trap_time = 30
ban_time = 2*60
turned = False
victims = dict()

allowed = ('c_a_k_e', 'a_o_w', 'nastjanastja')
say = ('/me Рагнарос выходит на стол!', '/me Рагнарос покидает доску!')


# ban someone
def make_hit():
    if victims:
        vic = random.choice(list(victims.keys()))
        #print('>>>' + vic)
        return [
            '/timeout {0} {1}'.format(vic, ban_time),
            'Рагнарос попал в тебя, {0}!'.format(vic)
        ]
    else:
        return ''


switch_state = lambda x: True if x == 'on' else False


def ragnaros(args, chan, username):
    global turned
    global last_time_hit
    if chan == '#c_a_k_e':
        if args and args[0] == 'check':
            #print('>>> checking')
            remove = [x for x in victims if time.time() - victims[x] >= get_in_trap_time]
            for x in remove:
                victims.pop(x, None)

            #print(json.dumps(victims, indent=4))

            if turned:
                if time.time() - last_time_hit >= hit_freq:
                    #print('>> It is time to ban someone!')
                    last_time_hit = time.time()
                    return make_hit()
            return ''

        if args and args[0] == 'add':
            if args[1] not in allowed:
                victims[args[1]] = time.time()
            return ''

        if args and args[0] in ('on', 'off') and username in allowed:
            turned = switch_state(args[0])
            return [
                '/color {0}'.format(color),
                say[0] if turned else say[1],
                '/color Blue'
            ]

        if username in allowed:
            return make_hit()
        else:
            return ''
