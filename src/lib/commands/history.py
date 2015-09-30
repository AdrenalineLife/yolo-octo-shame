# -*- coding: utf-8 -*-
__author__ = 'Life'

import requests
import json
import time


class Channel(object):
    def __init__(self, name, break_time=1200):
        self.name = name
        self.is_online = False
        self.started = False
        self.curr_game = ''

        # время offline, за которое список игр не обнуляется (default 20 m)
        self.break_time = break_time

        # время, когда стрим становится offline
        self.time_ = 0

        # список игр, которые были на стриме
        self.games = []

    def get_state(self):
        req = 'https://api.twitch.tv/kraken/streams/{0}'
        resp = requests.get(req.format(self.name), timeout=3).json()
        self.is_online = resp['stream'] is not None
        self.curr_game = resp['stream']['channel']['game'] if self.is_online else ''
        #print(self.curr_game)

    def shorten_game(self):
        short_names = {
            'Counter-Strike: Global Offensive': 'CS:GO',
            'Counter-Strike: Source': 'CS Source',
            'Hearthstone: Heroes of Warcraft': 'Hearthstone',
            'World of Warcraft': 'WoW'
        }
        return short_names.get(self.curr_game, self.curr_game)

    def add_game(self):
        game_name = self.shorten_game()
        if self.games:
            if self.games[-1] != game_name:
                self.games.append(game_name)
                #print('Adding >> ' + game_name)
        else:
            self.games.append(game_name)
            #print('Adding >> ' + game_name)

    def expired(self):
        return time.time() - self.time_ > self.break_time


# значение break_time можно и не указывать (20 минут по умолч.)
ch_list = [
    Channel('a_o_w', 5*60)
]


def history(args, chan, username):
    if args and args[0] == 'check':
        for ch in ch_list:
            try:
                ch.get_state()
            except Exception:  # ConnectionError, ConnectTimeout
                continue
            if ch.is_online:
                ch.add_game()
                ch.started = True
            else:
                if ch.started:
                    ch.time_ = time.time()
                    ch.started = False
                if ch.expired():
                    ch.games = []
        return ''

    for ch in ch_list:
        if ch.name == chan[1:]:
            if ch.games:
                return ' -> '.join(ch.games)
            else:
                return 'Игор не было'