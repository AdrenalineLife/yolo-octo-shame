# -*- coding: utf-8 -*-
import time
import pickle

red = "\033[01;31m{0}\033[00m"
grn = "\033[01;36m{0}\033[00m"
blu = "\033[01;34m{0}\033[00m"
cya = "\033[01;36m{0}\033[00m"

clr = False  # Use colouring or not


def pp(message, mtype='INFO'):
    mtype = mtype.upper()

    if clr and mtype == "ERROR":
        mtype = red.format(mtype)

    print('[%s] [%s] %s' % (time.strftime('%H:%M:%S', time.localtime()), mtype, message))


def ppi(channel, message, username):
    username = grn.format(username) if clr else username
    msg = '[%s %s] <%s> %s' % (time.strftime('%H:%M:%S', time.localtime()), channel, username, message)  # grn
    try:
        print(msg)
    except UnicodeEncodeError as detail:
        pp('UnicodeEncodeError: %s' % detail, 'error')
    except UnicodeDecodeError as detail:
        pp('UnicodeDecodeError: %s' % detail, 'error')


def pbot(message, channel=''):
    bot = red.format('BOT') if clr else 'BOT'
    if channel:
        msg = '[%s %s] <%s> %s' % (time.strftime('%H:%M:%S', time.localtime()), channel, bot, message)  # red
    else:
        msg = '[%s] <%s> %s' % (time.strftime('%H:%M:%S', time.localtime()), bot, message)  # red
    try:
        print(msg)  # print(msg.encode(sys.stdout.encoding, errors='replace'))
    except UnicodeEncodeError as detail:
        pp('UnicodeEncodeError: %s' % detail, 'error')
    except UnicodeDecodeError as detail:
        pp('UnicodeDecodeError: %s' % detail, 'error')


def save_obj(obj, name):
    file_ = open(r'input_output\{}'.format(name), mode='wb')
    pickle.dump(obj, file_, 3)
    file_.close()


def load_obj(name):
    file_ = open(r'input_output\{}'.format(name), mode='rb')
    result = pickle.load(file_)
    file_.close()
    return result
