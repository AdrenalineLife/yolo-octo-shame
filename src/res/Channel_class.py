# -*- coding: utf-8 -*-
__author__ = 'Life'

import json
import time

import src.res.shorten_games as shorten_games


class Channel(object):
    def __init__(self, name, headers, break_time=630):
        self.name = name.lower()
        self.is_online = False
        self.started = False
        self.curr_game = ''

        # headers of api call
        self.api_headers = headers

        # время offline, за которое список игр не обнуляется
        self.break_time = break_time

        # время, когда стрим становится offline
        self.time_ = 0

        # список игр, которые были на стриме
        self.games = []

        # текущее количество зрителей
        self.viewers = 0

        # пик зрителей за стрим
        self.max_viewers = 0

        # время начала стрима
        self.created_at = ''

        # время начала стрима с перерывами
        self.created_at_withbreak = ''

        self.video_height = 0
        self.fps = 0
        self.delay = 0
        self.status = ''

    def get_state(self, chan_info):
        self.is_online = chan_info is not None
        if self.is_online:
            self.curr_game = chan_info['channel']['game']
            self.viewers = chan_info['viewers']
            self.created_at = chan_info['created_at']
            self.video_height = chan_info['video_height']
            self.fps = chan_info['average_fps']
            self.delay = chan_info['delay']
            self.status = chan_info['channel']['status']
            if self.viewers > self.max_viewers:
                self.max_viewers = self.viewers
            if not self.created_at_withbreak:
                self.created_at_withbreak = self.created_at

    def shorten_game(self):
        return shorten_games.shorten.get(self.curr_game, self.curr_game)

    def add_game(self):
        game_name = self.shorten_game()
        if self.games:
            if self.games[-1]['game'] != game_name:
                self.games[-1]['ended'] = time.time()
                self.games.append({'game': game_name, 'started': time.time()})
        else:
            self.games.append({'game': game_name, 'started': time.time()})

    def expired(self):
        return time.time() - self.time_ > self.break_time

    @staticmethod
    def to_str_w_time(x):  # for "games_to_str" with time
        m, s = divmod(int(x['ended'] - x['started']), 60)
        h, m = divmod(m, 60)
        return '{} [{} h {} m]'.format(x['game'], h, m) if h else '{} [{} m]'.format(x['game'], m)

    def games_to_str(self, need_time=False):
        if self.games:
            self.games[-1]['ended'] = time.time()
            if not need_time:
                return ' → '.join(x['game'] for x in self.games)
            else:
                return ' → '.join(self.to_str_w_time(x) for x in self.games)
        else:
            return 'Игр не было'

    def clear_games_list(self):
        self.games[:] = []

    # delete a game by index from list of games
    def del_game(self, index):
        del self.games[index]

    def __repr__(self):
        return json.dumps(self.__dict__, indent=4)
