# -*- coding: utf-8 -*-
__author__ = 'Life'

import requests
import re

from src.lib.functions_general import pp

bg_nick = {
    '#c_a_k_e': 'CakeDestroyer',
    '#': ''
}

type_full = {  # value is lowercase
    's': 'solo',
    'd': 'duo',
    'sq': 'squad',
    'solo': 'solo',
    'squad': 'squad',
    'duo': 'duo'
}

USAGE = '/w (sender) !bgrank s | d | sq'
LINK = 'https://pubg.me/{}'
STATS = ('rating', 'rounds', 'wins', 'kills', 'top10', 'rank')
REGEX = (
    r'<div.*? id="overview-eu".*?<div class="stat-h"><div>{} rating</div><div>([0-9]+)</div></div>',
    r'<div.*? id="overview-eu".*?<div class="stat-e"><div>{} rounds played</div><div>([0-9]+)</div></div>',
    r'<div.*? id="overview-eu".*?<div class="stat-h stat-md"><div>{} wins</div><div>([0-9]+)</div></div>',
    r'<div.*? id="overview-eu".*?<div class="stat-h stat-md"><div>{} kills</div><div>([0-9]+)</div></div>',
    r'''<div.*? id="overview-eu".*?<div class="stat-h stat-md"><div>{} top 10's</div><div>([0-9]+)</div></div>''',
    r'<div.*? id="overview-eu".*?<div class="stat-e"><div>{} rank in eu</div><div class="stat-r">(#[0-9]+)</div></div>'
)
RESP = 'PUBG {type}: Rank {rank}, Rounds {rounds}, Wins {wins}, Kills {kills}, Top 10: {top10}'


def bgrank(self, args, msg):
    nick = bg_nick.get(msg.chan, None)
    if nick is None:
        return ''

    if args:
        if args[0].lower() in ('s', 'd', 'sq', 'solo', 'duo', 'squad'):
            game_type = args[0].lower()
        else:
            return USAGE
    else:
        game_type = 's'
    game_type_full = type_full[game_type]

    try:
        page = requests.get(LINK.format(nick)).text
        stats = {stat: re.search(r, page).group(1) for stat, r in
                 zip(STATS, (x.format(game_type_full) for x in REGEX))}
        return RESP.format(type=game_type_full.capitalize(), **stats)
    except (requests.RequestException, AttributeError) as e:
        pp('bgrank: ' + str(e))

if __name__ == '__main__':
    class m: pass
    n = m(); n.chan = '#c_a_k_e'
    print(bgrank(None, ['s'], n))
    print(bgrank(None, ['d'], n))
    print(bgrank(None, ['sq'], n))
