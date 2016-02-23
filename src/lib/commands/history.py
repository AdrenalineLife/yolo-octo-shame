# -*- coding: utf-8 -*-
__author__ = 'Life'

import requests
import json
import time

from src.res.Channel_class import *


def history(args, msg):
    for ch in ch_list:
        if ch.name == msg.chan[1:]:
            return ch.games_to_str()
    return ''