# -*- coding: utf-8 -*-
__author__ = 'Life'

import time
import random
import json


color = 'Red'  # color for using /me
hit_freq = float(90)  # ban every hit_freq seconds
last_time_hit = 0
get_in_trap_time = float(30)
ban_time = 40
turned_on = False
victims = dict()

allowed = ('c_a_k_e', 'a_o_w', 'nastjanastja')
protected = ('c_a_k_e', 'a_o_w', 'nastjanastja', 'seeskixbocta', 'moobot', 'mirrobot', 'etozhemad')

say = ('/me Рагнарос выходит на стол!', '/me Рагнарос покидает доску!')


# ban someone
def make_hit(t=ban_time):
    if victims:
        vic = random.choice(list(victims.keys()))
        #print('>>> ' + vic + ' ' + str(t))
        return [
            '/timeout {0} {1}'.format(vic, t),
            'Рагнарос попал в тебя, {0}!'.format(vic)
        ]
    else:
        return ''


switch_state = lambda x: True if x == 'on' else False


def ragnaros(args, chan, username):
    global turned_on
    global last_time_hit
    global hit_freq
    global ban_time
    if chan == '#c_a_k_e':
        if args:
            if args[0] == 'check':
                #print('>>> checking')
                remove = [x for x in victims if time.time() - victims[x] >= get_in_trap_time]
                for x in remove:
                    victims.pop(x, None)

                #print(json.dumps(victims, indent=4))

                if turned_on and time.time() - last_time_hit >= hit_freq:
                    last_time_hit = time.time()
                    return make_hit()
                return ''

            if args[0] == 'add':
                if args[1] not in protected:
                    victims[args[1]] = time.time()
                return ''

            if args[0] in ('on', 'off') and username in allowed:
                turned_on = switch_state(args[0])
                last_time_hit = time.time()
                return [
                    '/color {0}'.format(color),
                    say[0] if turned_on else say[1],
                    '/color Blue'
                ]

            try:
                sec = int(args[0])
            except ValueError:
                return ''
            if sec < 5:
                sec = 5
            if username in allowed:
                make_hit(sec)

            if len(args) == 2 and username in allowed:
                if args[0] in ('cd', 'bantime'):
                    try:
                        sec = int(args[1])
                    except ValueError:
                        return ''
                    if sec > 4:
                        if args[0] == 'cd':
                            hit_freq = float(sec)
                        else:
                            ban_time = sec
                return ''

        if username in allowed:
            return make_hit()
        else:
            return ''
