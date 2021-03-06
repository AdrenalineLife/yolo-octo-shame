# -*- coding: utf-8 -*-
__author__ = 'Life'

import shutil
import json
import time
import os
import datetime as dt

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator

import src.res.shorten_games as shorten_games
from src.lib.functions_general import pp


def get_interval(duration):
    if duration < 300:
        return 60
    if duration < 600:
        return 180
    if duration < 1800:
        return 300
    if duration < 3600:
        return 600
    if duration < 36000:
        return 3600
    if duration < 24 * 3600:
        return 3600 * 2
    return 3600 * 4


def get_labelinfo(interval):
    if interval < 3600:
        return (interval // 60), 'm'
    else:
        return (interval // 3600), 'h'


def normalize_game(game):
    game = shorten_games.shorten.get(game, game)
    if len(game) > 32:
        game = game[:25] + '…'
    return game


class Channel(object):
    def __init__(self, name, headers, break_time=500):
        self.chan_id = ''
        self.name = name.lower()
        self.is_online = False
        self.started = False
        self.curr_game = ''

        self.disp_name = ''

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
        self._last_time_updated = time.time()

        self.video_height = 0
        self.fps = 0
        self.delay = 0
        self.status = ''

        self.viewer_list = []
        self.plot_game_list = []

    def set_info(self, chan_info):
        self.is_online = chan_info is not None
        if self.is_online:
            self.disp_name = chan_info['channel']['display_name']
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
                self.created_at_dt = dt.datetime.strptime(self.created_at, '%Y-%m-%dT%H:%M:%SZ')
            if self.created_at_withbreak_dt is None:
                self.created_at_withbreak_dt = dt.datetime.strptime(self.created_at, '%Y-%m-%dT%H:%M:%SZ')
            if not self.created_at_withbreak:
                self.created_at_withbreak = self.created_at

            self.add_plot_point()
            self._last_time_updated = time.time()
            if len(self.viewer_list) % 20 == 0:
                self.make_plot()

    def check_state(self):
        if self.is_online:
            self.add_game()
            self.add_plot_game()
            self.started = True
            if self._started_tracking is None:
                self._started_tracking = dt.datetime.utcnow()
        else:
            if self.started:  # if the stream went offline recently
                self.make_plot()
                self.viewer_list = []
                self.games[-1]['ended'] = time.time()
                self.plot_game_list = []
                self._offline_ts = time.time()
                self.started = False
                self._started_tracking = None
                self.created_at_dt = None
            if self.expired():  # if the stream has ended a "long" time ago, thus break time expired
                self.games = []
                self.plot_game_list = []
                self.max_viewers = 0
                self.created_at_withbreak = ''
                self.created_at_withbreak_dt = None
                self._started_tracking = None

    def init_on_load(self):
        if time.time() - self._last_time_updated > 170.0 and self.viewer_list:
            pp('Viewer list was cleared ({})'.format(self.name))
            self._started_tracking = None
            self.viewer_list = []
            self.plot_game_list = []
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

    def add_plot_game(self):
        if self.plot_game_list:
            if self.plot_game_list[-1][0] != self.curr_game:
                self.plot_game_list.append((self.curr_game, dt.datetime.utcnow()))
        else:
            self.plot_game_list.append((self.curr_game, dt.datetime.utcnow()))

    def expired(self):
        return time.time() - self._offline_ts > self.break_time

    def uptime(self, with_break=False):  # in seconds
        now_ = dt.datetime.utcnow()
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
            return ''

    def clear_games_list(self):
        self.games[:] = []

    # delete a game by index from list of games
    def del_game(self, index):
        del self.games[index]

    def add_plot_point(self):
        if self.is_online:
            self.viewer_list.append(self.viewers)

    def make_plot(self, copy_plot=True):
        results_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'input_output', self.name)
        if not os.path.isdir(results_dir):
            os.makedirs(results_dir)

        file_name = r'plot_{0}_{1}.png'.format(self.name, self._started_tracking.strftime('%d-%m_%H-%M'))
        full_path = os.path.join(results_dir, file_name)

        N = len(self.viewer_list)
        dur = int((dt.datetime.utcnow() - self._started_tracking).total_seconds())
        interval = get_interval(dur)
        sec_start = int((self._started_tracking - self.created_at_dt).total_seconds()) % interval
        step = int(interval / dur * N)
        offset = int(sec_start / dur * N)
        z, lbl = get_labelinfo(interval)

        if N < 6:
            return None
        if not step:
            return None

        avg = sum(self.viewer_list) / N
        if avg < 20:
            avg = round(avg, 2)
        else:
            avg = int(avg)

        upper_title = self.status
        lower_title = '{0} {1} UTC, max: {2}, average: {3}'.format(self.disp_name,
                                                                   self.created_at_dt.strftime('%d.%m %H:%M'),
                                                                   max(self.viewer_list),
                                                                   avg)

        plt.cla()  # clear the axes
        ax.xaxis.set_minor_locator(AutoMinorLocator(2))
        ax.plot(self.viewer_list)
        ax.set_title('{}\n{}'.format(upper_title, lower_title), loc='left')

        for game, game_started in self.plot_game_list:
            pos = (game_started - self._started_tracking).total_seconds() / dur
            # put the name of a game
            ax.text(pos, -0.04,
                    normalize_game(game),
                    ha='right', va='top',
                    rotation='40', fontsize=8,
                    transform=ax.transAxes)
            # vertical line to indicate the start of a new game
            ax.axvline(N * pos, 0.02, 0.98, ls='--', lw=1, alpha=0.3, c='black')
        ax.axis([0, N - 1, 0, int(max(self.viewer_list) * 1.07)])
        ax.xaxis.set_ticks([x - offset for x in range(0, N*2, step) if 0 <= x - offset < N])
        ax.xaxis.set_ticklabels(['{}{}'.format(z * x, lbl)
                                 for x, _ in enumerate(ax.xaxis.get_major_ticks(), 1)])

        # fig.subplots_adjust(bottom=0.25)
        try:
            fig.savefig(full_path, bbox_inches='tight', dpi=100)
            if copy_plot:
                self.copy_plot(full_path, 'all-plots-static')
            return full_path
        except Exception as e:
            pp('Failed to save "{}" plot. {}: {}'.format(self.disp_name, e.__class__.__name__, str(e)),
               mtype='error')
            return None

    def copy_plot(self, plot_path, folder_name):
        dest_dir = os.path.join(plot_path, '..', '..', folder_name)
        if not os.path.isdir(dest_dir):
            os.makedirs(dest_dir)
        dest_path = os.path.join(dest_dir, 'plot_{}.png'.format(self.name))

        try:
            return shutil.copyfile(plot_path, dest_path)
        except (shutil.SameFileError, OSError) as e:
            pp('Failed to copy "{}" plot. {}: {}'.format(self.disp_name, e.__class__.__name__, str(e)),
               mtype='error')
            return None

    def __repr__(self):
        return json.dumps(self.__dict__, indent=4)


# these are general settings for axes,
# set when this file is imported

fig, ax = plt.subplots(1, 1, figsize=(11, 6))
ax.tick_params(axis='x', which='both', labelsize=7)
ax.xaxis.set_tick_params(direction='in', top=True, which='both')
ax.yaxis.set_tick_params(right=True)
