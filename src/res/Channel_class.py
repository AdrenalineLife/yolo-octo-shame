# -*- coding: utf-8 -*-
__author__ = 'Life'

import json
import time
import datetime
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator

import src.res.shorten_games as shorten_games


def get_interval(duration):
    if duration < 600:
        return 180
    if duration < 1800:
        return 300
    if duration < 3600:
        return 600
    if duration < 36000:
        return 3600
    if duration < 24*3600:
        return 3600*2
    return 3600*4

def get_labelinfo(interval):
    if interval < 3600:
        return (interval // 60), 'm'
    else:
        return (interval // 3600), 'h'

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
        self._offline_ts = 0

        # список игр, которые были на стриме
        self.games = []

        # текущее количество зрителей
        self.viewers = 0

        # пик зрителей за стрим
        self.max_viewers = 0

        # время начала стрима
        self.created_at = ''
        self.created_at_dt = None  # as a datetime

        # время начала стрима с перерывами
        self.created_at_withbreak = ''
        self.created_at_withbreak_dt = None  # as a datetime

        self._started_tracking = None
        self._last_time_updated = None

        self.video_height = 0
        self.fps = 0
        self.delay = 0
        self.status = ''

        self.viewer_list = []

    def set_info(self, chan_info):
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
            if self.created_at_dt is None:
                self.created_at_dt = datetime.datetime.strptime(self.created_at, '%Y-%m-%dT%H:%M:%SZ')
            if self.created_at_withbreak_dt is None:
                self.created_at_withbreak_dt = datetime.datetime.strptime(self.created_at, '%Y-%m-%dT%H:%M:%SZ')
            if not self.created_at_withbreak:
                self.created_at_withbreak = self.created_at

            self.plot_stuff()
            self._last_time_updated = time.time()
            if len(self.viewer_list) % 100 == 0:
                self.make_plot()

    def check_state(self):
        if self.is_online:
            self.add_game()
            self.started = True
            if self._started_tracking is None:
                self._started_tracking = datetime.datetime.utcnow()
        else:
            if self.started:
                self.make_plot()
                self.viewer_list = []
                self.games[-1]['ended'] = time.time()
                self._offline_ts = time.time()
                self.started = False
                self._started_tracking = None
            if self.expired():
                self.games = []
                self.max_viewers = 0
                self.created_at_withbreak = ''
                self.created_at_withbreak_dt = None
                self._started_tracking = None

    def init_on_load(self):
        if time.time() - self._last_time_updated > 120:
            self._started_tracking = None
            self.viewer_list = []
        self.started = False
        self.created_at_withbreak_dt = None
        self.created_at_dt = None

    def shorten_game(self, game):
        return shorten_games.shorten.get(game, game)

    def add_game(self):
        if self.games:
            if self.games[-1]['game'] != self.curr_game:
                self.games[-1]['ended'] = time.time()
                self.games.append({'game': self.curr_game, 'started': time.time()})
        else:
            self.games.append({'game': self.curr_game, 'started': time.time()})

    def expired(self):
        return time.time() - self._offline_ts > self.break_time

    def uptime(self, with_break=False):  # in seconds
        now_ = datetime.datetime.utcnow()
        if with_break:
            return (now_ - self.created_at_withbreak_dt).total_seconds()
        else:
            return (now_ - self.created_at_dt).total_seconds()

    def to_str_w_time(self, x):  # for "games_to_str" with time
        m, s = divmod(int(x['ended'] - x['started']), 60)
        h, m = divmod(m, 60)
        if h:
            return '{} [{} h {} m]'.format(self.shorten_game(x['game']), h, m)
        else:
            return '{} [{} m]'.format(self.shorten_game(x['game']), m)

    def games_to_str(self, need_time=False, separator=' → '):
        if self.games:
            self.games[-1]['ended'] = time.time()
            if not need_time:
                return separator.join(self.shorten_game(x['game']) for x in self.games)
            else:
                return separator.join(self.to_str_w_time(x) for x in self.games)
        else:
            return 'Игр не было'

    def clear_games_list(self):
        self.games[:] = []

    # delete a game by index from list of games
    def del_game(self, index):
        del self.games[index]

    def plot_stuff(self):
        if self.is_online:
            self.viewer_list.append(self.viewers)
        elif self.started:
            pass
            '''f_ = open(r'input_output\{}\plot_{}_{}.txt'.format(self.name, self.name, self.created_at.replace(':', '-')), 'wt')
            f_.write('{}'.format(int(self.uptime())))
            f_.write(str(self.viewers) + '\n')
            f_.close()'''

    def make_plot(self):
        name = 'input_output\plot_{0}_{1}.png'.format(self.name, time.strftime('%m-%d_%H-%M-%S', time.localtime()))

        N = len(self.viewer_list)
        dur = int((datetime.datetime.utcnow() - self._started_tracking).total_seconds())
        interval = get_interval(dur)
        sec_start = int((self._started_tracking - self.created_at_dt).total_seconds()) % interval
        step = int(interval / dur * N)
        offset = int(sec_start / dur * N)

        z, lbl = get_labelinfo(interval)

        if N < 10:
            return None
        if not step:
            return None

        #fig, ax = plt.subplots(1, 1)
        ax.plot(self.viewer_list)
        '''ax.text(0.55, -0.05, 'matplotlib фыва asddsggd', horizontalalignment='right',
                verticalalignment='top',
                rotation='35',
                fontsize=8,
                transform=ax.transAxes)'''
        #ax.tick_params(axis='x', which='both', labelsize=7)
        ax.axis([0, N - 1, 0, int(max(self.viewer_list) * 1.07)])
        #ax.xaxis.set_minor_locator(AutoMinorLocator(2))
        #ax.xaxis.set_tick_params(direction='in', top=True, which='both')
        ax.xaxis.set_ticks([x - offset for x in range(0, N*2, step) if 0 <= x - offset < N])
        ax.xaxis.set_ticklabels(['{}{}'.format(z*x, lbl) for x, _ in enumerate(ax.xaxis.get_major_ticks(), 1)])
        #ax.yaxis.set_tick_params(right=True)

        #fig.subplots_adjust(bottom=0.25)
        fig.savefig(name, bbox_inches='tight')

    def __repr__(self):
        return json.dumps(self.__dict__, indent=4)


fig, ax = plt.subplots(1, 1, figsize=(11, 6), dpi=100)
ax.tick_params(axis='x', which='both', labelsize=7)
ax.xaxis.set_minor_locator(AutoMinorLocator(2))
ax.xaxis.set_tick_params(direction='in', top=True, which='both')
ax.yaxis.set_tick_params(right=True)
