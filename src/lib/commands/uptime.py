# -*- coding: utf-8 -*-
__author__ = 'Life'

import datetime

import src.res.shorten_games as shorten_games


def uptime(self, args, msg):
    try:
        chan = next(x for x in self.ch_list if x.name == msg.chan[1:])
        if not chan.is_online:
            return ''
        diff = datetime.datetime.utcnow() - datetime.datetime.strptime(chan.created_at, '%Y-%m-%dT%H:%M:%SZ')
    except (StopIteration, ValueError):
        return ''

    curr_game = shorten_games.shorten.get(chan.curr_game, chan.curr_game)
    h, m = divmod(diff.seconds, 3600)
    m, s = divmod(m, 60)

    timestr = '{m:0>2}:{s:0>2}'
    if diff.days:
        timestr = '{d} дней {h:0>2}:{m:0>2}:{s:0>2}'
    elif h:
        timestr = '{h:0>2}:{m:0>2}:{s:0>2}'
    resp = 'Стрим идет %s | Игра: {g} | Смотрит {v}' % timestr
    if chan.max_viewers and chan.max_viewers > chan.viewers:
        resp += ' | Пик {max}'
    return resp.format(d=diff.days, h=h, m=m, s=s, v=chan.viewers, g=curr_game, max=chan.max_viewers)
