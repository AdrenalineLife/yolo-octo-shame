# -*- coding: utf-8 -*-
__author__ = 'Life'

import os
import pickle
import datetime as dt


ALLOWED = ()
FILENAME = 'mat.p'
RESP_NEW = 'Продержался без матов: {diff}'  # when new date is set
RESP_DEFAULT = 'Времени прошло без матов: {diff}'
RESP_NODATE = 'Последняя дата неизвестна'
RESP_NEW_NODATE = ''

current_date = None
try:
    path = os.path.join('input_output', FILENAME)
    file_ = open(path, 'rb')
    current_date = pickle.load(file_)
    file_.close()
except (FileNotFoundError, IOError, ValueError):
    pass


def diff_tostr(d):
    h, m = divmod(d.seconds, 3600)
    m, s = divmod(m, 60)

    timestr = '{m} m {s} s'
    if d.days:
        timestr = '{d} дн. {h} h {m} m'
    elif h:
        timestr = '{h} h {m} m'
    return timestr.format(d=d.days, h=h, m=m, s=s)


def mat(self, args, msg):
    global current_date
    if msg.chan_id == '43899589':  # c_a_k_e
        if args and args[0].lower() == 'new':
            if msg.user_id in ALLOWED or msg.is_mod or msg.badges.get('subscriber', 0) == 24:
                if current_date is not None:
                    diff = diff_tostr(dt.datetime.utcnow() - current_date)
                    resp = RESP_NEW.format(diff=diff)
                else:
                    resp = RESP_NEW_NODATE
                current_date = dt.datetime.utcnow()
                path = os.path.join('input_output', FILENAME)
                file_ = open(path, 'wb')
                pickle.dump(current_date, file_)
                file_.close()
                return resp
        else:
            if current_date is not None:
                return RESP_DEFAULT.format(diff=diff_tostr(dt.datetime.utcnow() - current_date))
            else:
                return RESP_NODATE
