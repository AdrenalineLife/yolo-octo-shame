# -*- coding: utf-8 -*-
__author__ = 'Life'

import time
import random
import json


class Ragnaros(object):
    def __init__(self, name, color='Red', hit_freq=90.0, get_in_trap_time=30.0, ban_time=40.0):
        self.name = name.lower()
        self.color = color  # color for using /me
        self.hit_freq = hit_freq  # ban every hit_freq seconds
        self.last_time_hit = 0
        self.get_in_trap_time = get_in_trap_time
        self.ban_time = ban_time
        self.turned_on = False
        self.victims = dict()

    def make_hit(self, t=None):
        if t is None:
            t = self.ban_time
        if self.victims:
            vic = random.choice(list(self.victims.keys()))
            #print('>>> ' + vic + ' ' + str(t))
            return [
                '/timeout {0} {1}'.format(vic, t),
                'Рагнарос попал в тебя, {0}!'.format(vic)
            ]
        else:
            return ''

    def remove_users(self):
        remove = [x for x in self.victims if time.time() - self.victims[x] >= self.get_in_trap_time]
        for x in remove:
            self.victims.pop(x, None)


allowed = ('c_a_k_e', 'a_o_w', 'nastjanastja')
protected = ('c_a_k_e', 'a_o_w', 'nastjanastja', 'seeskixbocta', 'moobot', 'mirrobot', 'etozhemad')

say = ('/me Рагнарос выходит на стол!', '/me Рагнарос покидает доску!')


switch_state = lambda x: True if x == 'on' else False

ragn_list = [
    Ragnaros('#c_a_k_e'),
    Ragnaros('#meleeman777')
]


def ragnaros(args, chan, username):
    ragn = [x for x in ragn_list if x.name == chan]
    if not ragn:
        return ''
    else:
        ragn = ragn[0]
    if args:
        if args[0] == 'check':
            ragn.remove_users()
            #print(json.dumps(victims, indent=4))

            if ragn.turned_on and time.time() - ragn.last_time_hit >= ragn.hit_freq:
                ragn.last_time_hit = time.time()
                return ragn.make_hit()
            return ''

        if args[0] == 'add':
            if args[1] not in protected:
                ragn.victims[args[1]] = time.time()
            return ''

        if args[0] in ('on', 'off') and username in allowed:
            ragn.turned_on = switch_state(args[0])
            ragn.last_time_hit = time.time()
            return [
                '/color {0}'.format(ragn.color),
                say[0] if ragn.turned_on else say[1],
                '/color Blue'
            ]

        try:
            sec = int(args[0])
        except ValueError:
            return ''
        if sec < 5:
            sec = 5
        if username in allowed:
            ragn.make_hit(sec)

        if len(args) == 2 and username in allowed:
            if args[0] in ('cd', 'bantime'):
                try:
                    sec = int(args[1])
                except ValueError:
                    return ''
                if sec > 4:
                    if args[0] == 'cd':
                        ragn.hit_freq = float(sec)
                    else:
                        ragn.ban_time = sec
            return ''

    if username in allowed:
        return ragn.make_hit()
    else:
        return ''
