# -*- coding: utf-8 -*-
import time

red = "\033[01;31m{0}\033[00m"
grn = "\033[01;36m{0}\033[00m"
blu = "\033[01;34m{0}\033[00m"
cya = "\033[01;36m{0}\033[00m"

clr = False  # Use colouring or not


def pp(message, mtype='INFO'):
    mtype = mtype.upper()

    if mtype == "ERROR" and clr:
        mtype = red.format(mtype)

    print('[%s] [%s] %s' % (time.strftime('%H:%M:%S', time.localtime()), mtype, message))


def ppi(channel, message, username):
    msg = '[%s %s] <%s> %s' % (time.strftime('%H:%M:%S', time.localtime()), channel, grn.format(username) if clr else username, message)  # grn
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
