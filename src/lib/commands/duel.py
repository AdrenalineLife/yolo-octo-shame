# -*- coding: utf-8 -*-
__author__ = 'Life'
from requests import get
import json
import time
import random

import src.config.config as cfg


class Duel(object):
    def __init__(self, name, sec_name, seconds):
        self.first_duelist = name
        self.sec_duelist = sec_name
        self.ban_time = seconds
        self.time = time.time()

    @staticmethod
    def user_status(user, chan_name):
        chatters = get('http://tmi.twitch.tv/group/user/{0}/chatters'.format(chan_name)).json()['chatters']
        print(json.dumps(chatters, indent=4))
        all_mods = chatters['moderators'] + chatters['staff'] + chatters['admins'] + chatters['global_mods']
        is_mod = user in all_mods
        in_chat = True if is_mod else user in chatters['viewers']
        return in_chat, is_mod

    @staticmethod
    def max_reached(chan):
        return len(duels[chan]) >= max_d

    def make_duel(self):
        return random.choice([self.first_duelist, self.sec_duelist])

    def expired(self):
        return time.time() - self.time >= wait_time

    @staticmethod
    def has_active_duel(name, chan):
        z = [x for x in duels[chan] if name in (x.first_duelist, x.sec_duelist)]
        return bool(z)


def get_sec(s):
    try:
        s = int(s)
        if s > 5*60: s = 5*60
        if s < 20: s = 20
    except Exception:
        s = def_ban_time
    return s


def_ban_time = 30  # default ban time
wait_time = 23.0  # time to wait before cancelling unaccepted duel
max_d = 2  # maximum amount of simultaneous duels for each channel
turned_on = {x: True for x in cfg.config['channels']}
duels = {x: [] for x in cfg.config['channels']}
allowed_users = ('a_o_w', 'adrenaline_life', 'c_a_k_e', 'nastjanastja')

say_usage = "/w (sender) Напишите '!duel <username>' для вызова пользователя на дуэль." \
            " Через пробел можно указать время бана в сек (default={0})".format(def_ban_time)
say_expired = "/me > {1} так и не решился принять дуэль {0}"
say_max_reached = "/w (sender) Не допустимо больше {0} одновременных дуэлей на канале".format(max_d)
say_have_active = "/w (sender) Вы не можете использовать команду, т.к. у вас уже есть активная дуэль"
say_has_active = "/w (sender) Вы не можете вызвать этого пользователя, так как у него уже есть активная дуэль"
say_not_in_chat = "/w (sender) Пользователь '{0}' не найден в чате"
say_is_mod = "/me > {0}, у тебя кишка тонка вызвать {1}!"
say_you_is_mod = "/me > {0}, пощади смертного!"
say_new_duel = "/me > {0} вызвал {1} на дуэль! (бан: {2} сек)"
say_howto = "/w {1} {0} вызвал вас на дуэль. Напишите '!duel принять', чтобы принять вызов" \
            " или '!duel отклонить', чтобы слиться"
say_duel_result = "/me > {1} застрелил {0}!"
say_you_coward = "/me > {1} струсил и не принял вызов {0}"
say_now_restricted = "/me > {0} запретил дуэли законодательно!"
say_now_allowed = "/me > {0} официально разрешил дуэли"


def duel(args, chan, username):
    if args and args[0] in ('on', 'off'):
        if username in allowed_users:
            turned_on[chan] = True if args[0] == 'on' else False
            return say_now_allowed.format(username) if turned_on[chan] else say_now_restricted.format(username)
        return ''

    if args and args[0] == 'chk':
        d_list = [x for x in duels[chan] if x.expired()]
        resp = [say_expired.format(x.first_duelist, x.sec_duelist) for x in d_list]
        for x in d_list:
            duels[chan].remove(x)
        return resp

    if args and turned_on[chan]:
        arg1, arg2 = args[0].lower().lstrip('@'), get_sec(args[1]) if len(args) == 2 else def_ban_time
        if arg1 == 'принять':
            d_list = [x for x in duels[chan] if x.sec_duelist == username]
            if d_list:
                d = d_list[0]
                banned = d.make_duel()
                not_banned = d.first_duelist if d.first_duelist != banned else d.sec_duelist
                duels[chan].remove(d)
                return [
                    '/timeout {0} {1}'.format(banned, d.ban_time),
                    say_duel_result.format(banned, not_banned)
                ]
            else:
                return ''

        if arg1 == 'отклонить':
            d_list = [x for x in duels[chan] if x.sec_duelist == username]
            if d_list:
                d = d_list[0]
                duels[chan].remove(d)
                return say_you_coward.format(d.first_duelist, d.sec_duelist)
            else:
                return ''

        if not Duel.max_reached(chan):
            if not Duel.has_active_duel(username, chan):
                if not Duel.has_active_duel(arg1, chan):
                    in_chat, is_mod = Duel.user_status(arg1, chan[1:])
                    if in_chat:
                        if not is_mod:
                            is_mod = Duel.user_status(username, chan[1:])[1]
                            if not is_mod:
                                duels[chan].append(Duel(username, arg1, arg2))
                                return [
                                    say_new_duel.format(username, arg1, arg2),
                                    say_howto.format(username, arg1)
                                ]
                            else:
                                return say_you_is_mod.format(username, arg1)
                        else:
                            return say_is_mod.format(username, arg1)
                    else:
                        return say_not_in_chat.format(arg1)
                else:
                    return say_has_active
            else:
                return say_have_active
        else:
            return say_max_reached
    else:
        return say_usage


if __name__ == '__main__':
    print(Duel.user_status('adrenaline_life', 'nastjanastja'))
    print(Duel.user_status('a_o_w', 'nastjanastja'))
    print(Duel.user_status('c_a_k_e', 'nastjanastja'))
    print(Duel.max_reached('#a_o_w'))