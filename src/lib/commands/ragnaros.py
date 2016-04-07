# -*- coding: utf-8 -*-
__author__ = 'Life'

import time
import random
import json
from src.lib.functions_general import save_obj, load_obj, pp


class Ragnaros(object):
    def __init__(self, name, color='Red', hit_freq=90.0, get_in_trap_time=30.0, ban_time=40):
        self.name = name.lower()
        self.color = color  # color for using /me
        self.hit_freq = hit_freq  # ban every hit_freq seconds
        self.get_in_trap_time = get_in_trap_time
        self.ban_time = ban_time
        self.turned_on = False
        self.last_time_hit = 0.0
        self.victims = dict()

    def make_hit(self, t=None):
        if t is None:
            t = self.ban_time
        if self.victims:
            vic = random.choice(list(self.victims.keys()))
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

    def turn_on_off(self, s):
        self.turned_on = True if s == 'on' else False

    def __repr__(self):
        return json.dumps(self.__dict__, indent=0) #'{} {}'.format(self.name, self.turned_on)


allowed = ('c_a_k_e', 'a_o_w', 'nastjanastja', 'adrenaline_life')

say = ('/me > Рагнарос выходит на стол!', '/me > Рагнарос покидает доску!')

required_ch = (
    '#a_o_w',
)

try:
    ragn_list = load_obj('ragnaros')
except FileNotFoundError:
    ragn_list = [Ragnaros(x) for x in required_ch]
except Exception:
    ragn_list = [Ragnaros(x) for x in required_ch]
    pp("Could not load ragnaros file", 'error')
else:
    existing_ragn = [x.name for x in ragn_list]
    for x in required_ch:
        if x not in existing_ragn:
            ragn_list.append(Ragnaros(x))
    del existing_ragn
    for x in ragn_list:
        x.victims = dict()
        x.last_time_hit = time.time()


def ragnaros(args, msg):
    ragn = [x for x in ragn_list if x.name == msg.chan]
    if not ragn:
        return ''
    else:
        ragn = ragn[0]
    if args:
        if args[0] == 'check':
            ragn.remove_users()
            if ragn.turned_on and time.time() - ragn.last_time_hit >= ragn.hit_freq:
                ragn.last_time_hit = time.time()
                return ragn.make_hit()
            return ''

        if args[0] == 'add':
            if not msg.is_mod:
                ragn.victims[msg.name] = time.time()
            return ''

        if args[0] in ('on', 'off') and msg.name in allowed:
            ragn.turn_on_off(args[0])
            ragn.last_time_hit = time.time()
            save_obj(ragn_list, 'ragnaros')
            return [
                '/color {0}'.format(ragn.color),
                say[0] if ragn.turned_on else say[1],
                '/color Blue'
            ]

        if len(args) == 2 and msg.name in allowed:
            if args[0] in ('cd', 'bantime'):
                try:
                    sec = int(args[1])
                except ValueError:
                    return ''
                sec = 4 if sec < 4 else sec
                if args[0] == 'cd':
                    ragn.hit_freq = float(sec)
                    save_obj(ragn_list, 'ragnaros')
                else:
                    ragn.ban_time = sec
                    save_obj(ragn_list, 'ragnaros')
            return ''

        try:
            sec = int(args[0])
        except ValueError:
            return ''
        if sec < 5:
            sec = 5
        if msg.name in allowed:
            return ragn.make_hit(sec)

    if msg.name in allowed:
        return ragn.make_hit()
    else:
        return ''
