# -*- coding: utf-8 -*-
__author__ = 'Life'

import random

from numbers import Number
from math import *


def evl(self, args, msg):
    #__import__('importlib').import_module('src.res.shorten_games').shorten.update({'1': '2'})
    try:
        if (msg.user_id == '85413884' or msg.user_id == '54602374') and args:
            res = eval(' '.join(args))

            # check how we want to display it
            if hasattr(res, '__iter__'):
                if type(res) != str:
                    if all(type(x) == str for x in res):
                        return res
                    else:
                        return '/w (sender) Not all elems of iterable are string'
                else:
                    return res
            if isinstance(res, Number) or type(res) == bool:
                return str(res)

    except Exception as exc:
        return "/w (sender) {}: {}".format(exc.__class__.__name__, str(exc))
