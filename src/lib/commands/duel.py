# -*- coding: utf-8 -*-
__author__ = 'Life'

from requests import get
import json
import time
import random

import src.config.config as cfg

# TODO переписать
class Duel(object):
    def __init__(self, name, sec_name, seconds):
        self.first_name_disp = name.lstrip('@')
        self.first_name = self.first_name_disp.lower()
        self.sec_name_disp = sec_name.lstrip('@')
        self.sec_name = self.sec_name_disp.lower()
        self.ban_time = seconds
        self.time = time.time()

    @staticmethod
    def max_reached(chan):
        return len(duels[chan]) >= max_d

    def make_duel(self):
        return random.choice([self.first_name_disp, self.sec_name_disp])

    def expired(self):
        return time.time() - self.time >= wait_time

    @staticmethod
    def has_active_duel(name, chan):
        return bool([x for x in duels[chan] if name in (x.first_name, x.sec_name)])


def user_status(user, chan_name):
    link = 'http://tmi.twitch.tv/group/user/{0}/chatters'
    try:
        chatters = get(link.format(chan_name), timeout=6).json()['chatters']
    except Exception:
        return False, False
    all_mods = chatters['moderators'] + chatters['staff'] + chatters['admins'] + chatters['global_mods']
    is_mod = user in all_mods
    in_chat = True if is_mod else user in chatters['viewers']
    return in_chat, is_mod


def get_sec(s):
    try:
        s = int(s)
        if s > 5*60: s = 5*60
        if s < 20: s = 20
    except Exception:
        s = def_ban_time
    return s


def_ban_time = 60  # default ban time
wait_time = 33.0  # time to wait before cancelling unaccepted duel
max_d = 3  # maximum amount of simultaneous duels for each channel
turned_on = {x: True for x in cfg.config['channels']}
duels = {x: list() for x in cfg.config['channels']}
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
say_suicide = "/me > {0} совершил самоубийство"


def duel(args, msg):
    if args and args[0] in ('on', 'off'):
        if msg.name in allowed_users:
            turned_on[msg.chan] = True if args[0] == 'on' else False
            return say_now_allowed.format(msg.disp_name) if turned_on[msg.chan] else say_now_restricted.format(msg.disp_name)
        return ''

    if args and args[0] == 'chk':
        d_list = [x for x in duels[msg.chan] if x.expired()]
        resp = [say_expired.format(x.f_d_disp, x.sec_d_disp) for x in d_list]
        for x in d_list:
            duels[msg.chan].remove(x)
        return resp

    if turned_on[msg.chan]:
        if args:
            arg1, arg2 = args[0].lower().lstrip('@'), get_sec(args[1]) if len(args) == 2 else def_ban_time
            arg1_disp = args[0].lstrip('@')
            if arg1 == msg.name:
                return [
                    '/timeout {0} {1}'.format(msg.name, arg2),
                    say_suicide.format(msg.disp_name)
                ]

            if arg1 == 'принять':
                d_list = [x for x in duels[msg.chan] if x.sec_name == msg.name]
                if d_list:
                    d = d_list[0]
                    banned = d.make_duel()
                    not_banned = d.first_name_disp if d.first_name_disp != banned else d.sec_name_disp
                    duels[msg.chan].remove(d)
                    return [
                        '/timeout {0} {1}'.format(banned, d.ban_time),
                        say_duel_result.format(banned, not_banned)
                    ]
                else:
                    return ''

            if arg1 == 'отклонить':
                d_list = [x for x in duels[msg.chan] if x.sec_name == msg.name]
                if d_list:
                    d = d_list[0]
                    duels[msg.chan].remove(d)
                    return say_you_coward.format(d.first_name_disp, d.sec_name_disp)
                else:
                    return ''

            if Duel.max_reached(msg.chan):
                return say_max_reached
            if Duel.has_active_duel(msg.name, msg.chan):
                return say_have_active
            if Duel.has_active_duel(arg1, msg.chan):
                return say_has_active
            in_chat, is_mod = user_status(arg1, msg.chan[1:])
            if not in_chat:
                return say_not_in_chat.format(arg1_disp)
            if is_mod:
                return say_is_mod.format(msg.disp_name, arg1_disp)
            #is_mod = user_status(msg.name, msg.chan[1:])[1]
            if msg.is_mod:
                return say_you_is_mod.format(msg.disp_name, arg1_disp)
            duels[msg.chan].append(Duel(msg.disp_name, arg1_disp, arg2))
            return [
                say_new_duel.format(msg.disp_name, arg1_disp, arg2),
                say_howto.format(msg.disp_name, arg1_disp)
            ]
        else:
            return say_usage


if __name__ == '__main__':
    print(user_status('adrenaline_life', 'nastjanastja'))
    print(user_status('a_o_w', 'nastjanastja'))
    print(user_status('c_a_k_e', 'nastjanastja'))
    print(Duel.max_reached('#a_o_w'))