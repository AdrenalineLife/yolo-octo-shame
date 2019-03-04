# -*- coding: utf-8 -*-

import time
import pickle

red = "\033[01;31m{0}\033[00m"
grn = "\033[01;36m{0}\033[00m"
blu = "\033[01;34m{0}\033[00m"
cya = "\033[01;36m{0}\033[00m"
yel = "\033[01;33m{0}\033[00m"

clr = False  # Use colouring or not


# for printing general information
def pp(message, mtype='INFO'):
    mtype = mtype.upper()

    if clr:
        if mtype == "ERROR":
            mtype = red.format(mtype)
        elif mtype == 'WARNING':
            mtype = yel.format(mtype)
    resp = '[{}] [{}] {}'.format(time.strftime('%H:%M:%S', time.localtime()), mtype, message)
    # if mtype in ('ERROR', 'WARNING'):
    #     f_ = open(r'input_output\pp.txt', 'at')
    #     f_.write(resp + '\r\n')
    #     f_.close()
    print(resp)


# for printing chat messages
def ppi(channel, message, username):
    username = grn.format(username) if clr else username
    msg = '[{} {}] <{}> {}'.format(time.strftime('%H:%M:%S', time.localtime()), channel, username, message)
    try:
        print(msg)
    except UnicodeEncodeError as detail:
        pp('UnicodeEncodeError: {}'.format(detail), mtype='error')
    except UnicodeDecodeError as detail:
        pp('UnicodeDecodeError: {}'.format(detail), mtype='error')


# for printing what the bot sends to chat
def pbot(message, channel=''):
    bot = red.format('BOT') if clr else 'BOT'
    if channel:
        msg = '[{} {}] <{}> {}'.format(time.strftime('%H:%M:%S', time.localtime()), channel, bot, message)
    else:
        msg = '[{}] <{}> {}'.format(time.strftime('%H:%M:%S', time.localtime()), bot, message)
    try:
        print(msg)  # print(msg.encode(sys.stdout.encoding, errors='replace'))
    except UnicodeEncodeError as detail:
        pp('UnicodeEncodeError: {}'.format(detail), mtype='error')
    except UnicodeDecodeError as detail:
        pp('UnicodeDecodeError: {}'.format(detail), mtype='error')


def save_obj(obj, name):
    file_ = open(r'input_output\{}.p'.format(name), mode='wb')
    pickle.dump(obj, file_, 3)
    file_.close()


def load_obj(name):
    file_ = open(r'input_output\{}.p'.format(name), mode='rb')
    result = pickle.load(file_)
    file_.close()
    return result
