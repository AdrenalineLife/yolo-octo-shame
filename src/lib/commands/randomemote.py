# -*- coding: utf-8 -*-
# coding: utf8

import random, json


def randomemote(args, chan, username):
    filename = 'src/res/global_emotes.json'

    try:
        data = json.loads(file(filename, 'r').read())
    except Exception:
        return 'Error reading %s.' % filename

    emote = random.choice(data.keys())
    return emote
