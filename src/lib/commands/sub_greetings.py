# -*- coding: utf-8 -*-
__author__ = 'Life'


greetings = {
    '#c_a_k_e': {
        'new': 'Приветствуем новобранца {n}!',
        'resub': 'Спасибо за подписку, {n}! {m} месяцев'
    },
    '#nastjanastja': {
        'new': 'Спасибо, {n}!',
        'resub': 'Спасибо за подписку, {n}! {m} месяцев'
    },
    '#': {
        'new': '',
        'resub': ''
    }
}

def sub_greetings(self, args, msg):
    global greetings
    chan, name, month = args
    try:
        resp = greetings[chan]['resub'] if month else greetings[chan]['new']
    except KeyError:
        return ''
    return resp.format(n=name, m=month) if month else resp.format(n=name)
