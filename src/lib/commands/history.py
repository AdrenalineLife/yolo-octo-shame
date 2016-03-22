# -*- coding: utf-8 -*-
__author__ = 'Life'

import requests
import json
import time

from src.res.Channel_class import *


def history(args, msg):
    ch = [x for x in ch_list if x.name == msg.chan[1:]]
    if not ch:
        return ''
    else:
        ch = ch[0]
    with_time = args and args[0] == 't'
    return ch.games_to_str(with_time)
