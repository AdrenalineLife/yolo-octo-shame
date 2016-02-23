# -*- coding: utf-8 -*-
__author__ = 'Life'

import json
import random

from src.lib.functions_general import pp

filename = 'src/res/emoticons.txt'
try:
    emotes = json.loads(open(filename).read())
    emotes = [el['regex'] for el in emotes['emoticons'] if el['regex'].isalpha()]
except Exception:
    pp('Ошибка при обработке файла смайлов (будут исп. несколько известных)', 'error')
    emotes = ['Kappa', 'Keepo', 'OpieOP', 'duDudu']

turned_on = {
    '#c_a_k_e': False,
    '#nastjanastja': False,
    '#adrenaline_life': False,
    '#a_o_w': False
}

allowed_users = (
    'a_o_w',
    'adrenaline_life',
    'c_a_k_e',
    'nastjanastja'
)


def pyramid(args, chan, username):
    if args[0] in ('on', 'off'):
        if username in allowed_users:
            turned_on[chan] = True if args[0] == 'on' else False
        return ''

    if turned_on[chan] or username in allowed_users:
        try:
            length = int(args[0])
        except Exception:
            return ''

        if length > 5:
            length = 5
        if length < 2:
            length = 2

        if len(args) == 2:
            word = args[1]
        else:
            word = random.choice(emotes)
        word += ' '
        res = [word * i for i in range(1, length + 1)]
        res += res[-2::-1]
        return res