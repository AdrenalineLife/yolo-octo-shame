# -*- coding: utf-8 -*-
__author__ = 'Life'

import requests
import json
import time

from src.res.Channel_class import *


def history(self, args, msg):
    ch = next(x for x in self.ch_list if x.name == msg.chan[1:])
    with_time = args and args[0] == 't'
    return ch.games_to_str(with_time)
