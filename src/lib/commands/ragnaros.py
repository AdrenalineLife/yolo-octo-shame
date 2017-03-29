# -*- coding: utf-8 -*-
__author__ = 'Life'

import time
import random
import json
import pickle

import src.config.config as cfg

from src.lib.functions_general import save_obj, load_obj, pp

'''This is a command to imitate ragnaros from Hearthstone.
Its purpose is to timeout a random person every 'hit_freq' secs when it is turned on.
It can also be explicitly called for a single hit.'''


class Ragnaros(object):
    def __init__(self, name, color='Red', hit_freq=90.0, get_in_trap_time=35.0, ban_time=40):
        self.name = name.lower()
        self.color = color  # color for using /me
        self.hit_freq = hit_freq  # ban every 'hit_freq' seconds
        self.get_in_trap_time = get_in_trap_time
        self.ban_time = ban_time
        self.turned_on = False
        self.last_time_hit = 0.0

    def choose_victim(self, iterable):
        t_ = time.time()
        sample = {x.disp_name for x in iterable
                  if t_ - x.created_ts < self.get_in_trap_time and not x.is_mod}
        if sample:
            return random.choice(list(sample))
        else:
            return ''

    def make_hit(self, messages, ban_time=None):
        if messages is not None:
            victim = self.choose_victim(messages)
        else:
            return ''
        if not victim:
            return ''
        if ban_time is None:
            ban_time = self.ban_time
        self.last_time_hit = time.time()
        return [
            '/timeout {0} {1}'.format(victim, ban_time),
            say_hit_you.format(disp_name=victim, ban=ban_time)
        ]

    def is_time_to_hit(self):
        return time.time() - self.last_time_hit >= self.hit_freq

    def turn_on_off(self, s):
        self.turned_on = True if s == 'on' else False

    def __repr__(self):
        return json.dumps(self.__dict__, indent=0)


say_is_on = '/me > Рагнарос выходит на стол!'
say_is_off = '/me > Рагнарос покидает доску!'
say_hit_you = 'Рагнарос попал в тебя, {disp_name}!'

required_ch = cfg.config['channels']

try:
    ragn_list = load_obj('ragnaros')
except FileNotFoundError:
    ragn_list = [Ragnaros(x) for x in required_ch]
except (pickle.PickleError, AttributeError, IndexError, EOFError):
    ragn_list = [Ragnaros(x) for x in required_ch]
    pp("Could not load ragnaros file", 'error')
else:
    loaded_ragn = [x.name for x in ragn_list]
    for x in required_ch:
        if x not in loaded_ragn:  # if required chan is not in the loaded list
            ragn_list.append(Ragnaros(x))  # then append it
    del loaded_ragn
    for x in ragn_list:
        x.last_time_hit = time.time()


def ragnaros(self, args, msg):
    ragn = next((x for x in ragn_list if x.name == msg.chan), False)
    if not ragn:
        return ''

    messages = self.chat_messages.get(msg.chan, None)
    if messages is None:
        pp('Channel {} was not found in chat messages (ragnaros.py)'.format(msg.chan), mtype='WARNING')

    if args:
        if args[0] == 'check':
            if ragn.turned_on and ragn.is_time_to_hit():
                return ragn.make_hit(messages)
            return ''

        if args[0] in ('on', 'off') and msg.is_mod:
            ragn.turn_on_off(args[0])
            ragn.last_time_hit = time.time()
            save_obj(ragn_list, 'ragnaros')
            return [
                '/color ' + ragn.color,
                say_is_on if ragn.turned_on else say_is_off,
                '/color ' + self.config['color']
            ]

        # setting some options
        if len(args) == 2 and msg.is_mod:
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
        if msg.is_mod:
            return ragn.make_hit(messages, ban_time=sec)
        return ''

    # explicit call without arguments
    if msg.is_mod:
        return ragn.make_hit(messages)
    else:
        return ''
