# -*- coding: utf-8 -*-
__author__ = 'Life'


import time

import requests
from random import randrange

import src.config.config as cfg
from src.lib.functions_general import pp


class Duel(object):
    def __init__(self, name, sec_name, seconds):
        self.first_name_disp = name.lstrip('@')
        self.first_name = self.first_name_disp.lower()
        self.sec_name_disp = sec_name.lstrip('@')
        self.sec_name = self.sec_name_disp.lower()
        self.ban_time = seconds
        self.created_ts = time.time()

    # return tuple (WINNER, LOSER)
    def make_duel(self):
        a = [self.first_name_disp, self.sec_name_disp]
        return a.pop(randrange(2)), a.pop()

    def expired(self):
        return time.time() - self.created_ts >= wait_time


def has_active_duel(name, chan):
    return any(1 for x in duels[chan] if name in (x.first_name, x.sec_name, x.first_name_disp, x.sec_name_disp))


def user_status(user, chan_name):
    link = 'http://tmi.twitch.tv/group/user/{0}/chatters'
    err_cnt = 0  # number of error occured while getting chatters
    done = False
    while not done:
        try:
            chatters = requests.get(link.format(chan_name), timeout=3).json()['chatters']
        except (requests.RequestException, KeyError):
            err_cnt += 1
            if err_cnt >= 3:
                return False, False
        else:
            done = True
    all_mods = chatters['moderators']
    all_mods.extend(chatters['staff'])
    all_mods.extend(chatters['admins'])
    all_mods.extend(chatters['global_mods'])
    is_mod = user in all_mods
    in_chat = True if is_mod else user in chatters['viewers']
    return in_chat, is_mod


def get_sec(s):
    try:
        s = int(s)
        if s > 5*60:
            s = 5*60
        if s < 20:
            s = 20
    except ValueError:
        s = def_ban_time
    return s


def_ban_time = 60  # default ban time
wait_time = 33.0  # time to wait before cancelling unaccepted duel
max_duels = 3  # maximum amount of simultaneous duels for each channel
turned_on = {x: False for x in cfg.config['channels']}
duels = {x: list() for x in cfg.config['channels']}  # dict of all duel of each channel
#killstreaks = {x: dict() for x in cfg.config['channels']}

say_usage = "/w (sender) Напишите '!duel <username>' для вызова пользователя на дуэль." \
            " Через пробел можно указать время бана в сек (default={0})".format(def_ban_time)
say_expired = "/me > {1} так и не решился принять дуэль {0}"
say_max_reached = "/w (sender) Не допустимо больше {0} одновременных дуэлей на канале".format(max_duels)
say_have_active = "/w (sender) Вы не можете использовать команду, т.к. у вас уже есть активная дуэль"
say_has_active = "/w (sender) Вы не можете вызвать этого пользователя, так как у него уже есть активная дуэль"
say_not_in_chat = "/w (sender) Пользователь '{0}' не найден в чате"
say_is_mod = "/me > {0}, у тебя кишка тонка вызвать {1}!"
say_you_is_mod = "/me > {0}, пощади смертного!"
say_new_duel = "/me > {0} вызвал {1} на дуэль! (бан: {2} сек). Напишите '!duel принять' или '!duel отклонить'"
say_howto = "/w {1} {0} вызвал вас на дуэль. Напишите '!duel принять', чтобы принять вызов" \
            " или '!duel отклонить', чтобы слиться"
say_duel_result = "/me > {1} застрелил {0}!"
say_you_coward = "/me > {1} струсил и не принял вызов {0}"
say_now_restricted = "/me > {0} запретил дуэли законодательно!"
say_now_allowed = "/me > {0} официально разрешил дуэли"
say_suicide = "/me > {0} совершил самоубийство"


def duel(self, args, msg):
    global def_ban_time, max_duels, turned_on, duels

    if args and args[0] in ('on', 'off'):
        if msg.is_mod:
            turned_on[msg.chan] = True if args[0] == 'on' else False
            return say_now_allowed.format(msg.disp_name) if turned_on[msg.chan] else say_now_restricted.format(msg.disp_name)
        return ''

    # automatic checking for outdated unaccepted duels
    if args and args[0] == 'chk':
        d_list = [x for x in duels[msg.chan] if x.expired()]
        resp = [say_expired.format(x.first_name_disp, x.sec_name_disp) for x in d_list]
        for x in d_list:
            duels[msg.chan].remove(x)
        return resp

    if turned_on[msg.chan]:
        if args:
            arg1_disp = args[0].lstrip('@')
            arg1 = arg1_disp.lower()
            arg2 = get_sec(args[1]) if len(args) == 2 else def_ban_time

            # in case of suicide
            if arg1 == msg.name:
                return [
                    '/timeout {0} {1}'.format(msg.name, arg2),
                    '/color Red',
                    say_suicide.format(msg.disp_name),
                    '/color ' + self.config['color']
                ]

            # accepting a duel
            if arg1 in ('принять', 'y'):
                duel_ = next((x for x in duels[msg.chan]
                              if x.sec_name == msg.name or x.sec_name_disp == msg.orig_disp_name), False)
                if duel_:
                    winner, loser = duel_.make_duel()
                    color_ = 'Green' if winner == duel_.first_name_disp else 'Red'
                    duels[msg.chan].remove(duel_)
                    return [
                        '/timeout {0} {1}'.format(loser, duel_.ban_time),
                        '/color ' + color_,
                        say_duel_result.format(loser, winner),
                        '/color ' + self.config['color']
                    ]
                else:
                    return ''

            # declining a duel
            if arg1 in ('отклонить', 'n'):
                duel_ = next((x for x in duels[msg.chan]
                              if x.sec_name == msg.name or x.sec_name_disp == msg.orig_disp_name), False)
                if duel_:
                    duels[msg.chan].remove(duel_)
                    return say_you_coward.format(duel_.first_name_disp, duel_.sec_name_disp)
                else:
                    return ''

            # checking conditions before creating a duel
            if msg.is_mod:
                return say_you_is_mod.format(msg.disp_name, arg1_disp)
            if len(duels[msg.chan]) >= max_duels:
                return ''
                #return say_max_reached
            if has_active_duel(msg.name, msg.chan):
                return say_have_active
            if has_active_duel(arg1, msg.chan):
                return say_has_active

            # looking up for user in chat's last messages
            try:
                t_ = time.time()
                victim = next(x for x in self.chat_messages[msg.chan]
                              if (x.name == arg1 or x.orig_disp_name == arg1_disp) and t_ - x.created_ts < 1200.0)
            except StopIteration:  # if no such message found
                in_chat, is_mod = user_status(arg1, msg.chan[1:])
            except KeyError as e:
                pp('Channel {} was not found in chat messages (duel.py)'.format(e), mtype='WARNING')
                return ''
            else:
                in_chat, is_mod = True, victim.is_mod

            if not in_chat:
                return say_not_in_chat.format(arg1_disp)
            if is_mod:
                return say_is_mod.format(msg.disp_name, arg1_disp)

            duels[msg.chan].append(Duel(msg.disp_name, arg1_disp, arg2))
            return [
                say_new_duel.format(msg.disp_name, arg1_disp, arg2),
                #say_howto.format(msg.disp_name, arg1_disp)
            ]
        else:
            return say_usage


if __name__ == '__main__':
    pass