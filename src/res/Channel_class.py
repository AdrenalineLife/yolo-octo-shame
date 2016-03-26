# -*- coding: utf-8 -*-
__author__ = 'Life'

import requests
import json
import time
import threading


class Channel(object):
    def __init__(self, name, break_time=1200):
        self.name = name.lower()
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

    def shorten_game(self):
        short_names = {
            'Counter-Strike: Global Offensive': 'CS:GO',
            'Counter-Strike: Source': 'CS Source',
            'Hearthstone: Heroes of Warcraft': 'Hearthstone',
            'World of Warcraft': 'WoW',
            "Tom Clancy's Rainbow Six: Siege": 'Rainbow Six: Siege'
        }
        return short_names.get(self.curr_game, self.curr_game)

    def add_game(self):
        game_name = self.shorten_game()
        if self.games:
            if self.games[-1]['game'] != game_name:
                self.games.append({'game': game_name, 'started': time.time()})
                #print('Adding >> ' + game_name)
        else:
            self.games.append({'game': game_name, 'started': time.time()})
            #print('Adding >> ' + game_name)

    def expired(self):
        return time.time() - self.time_ > self.break_time

    @staticmethod
    def to_str_w_time(x):  # for games_to_str with time
        m, s = divmod(int(x['ended'] - x['started']), 60)
        h, m = divmod(m, 60)
        return '{} [{} h {} m]'.format(x['game'], h, m) if h else '{} [{} m]'.format(x['game'], m)

    def games_to_str(self, need_time=False):
        if self.games:
            self.games[-1]['ended'] = time.time()
            if not need_time:
                return ' → '.join([x['game'] for x in self.games])
            else:
                return ' → '.join(self.to_str_w_time(x) for x in self.games) # доделать
        else:
            return 'Игр не было'


ch_list = [
    Channel('c_a_k_e'),
    Channel('nastjanastja'),
    Channel('a_o_w', 4*60)
]


def check_channel_state():
    while True:
        for ch in ch_list:
            try:
                ch.get_state()
                #print('got state of ' + ch.name)
            except Exception:  # ConnectionError, ConnectTimeout
                continue
            if ch.is_online:
                ch.add_game()
                ch.started = True
            else:
                if ch.started:
                    ch.games[-1]['ended'] = time.time()
                    ch.time_ = time.time()
                    ch.started = False
                if ch.expired():
                    ch.games = []
        time.sleep(8)

t = threading.Thread(target=check_channel_state, args=())
t.start()