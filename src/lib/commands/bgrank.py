# -*- coding: utf-8 -*-
__author__ = 'Life'

import requests
import json
import time

#from bs4 import BeautifulSoup

from src.lib.functions_general import pp

bg_nick = {  # PUBG nickname
    '#c_a_k_e': 'CakeDestroyer',
    '#': ''
}

default_type = {  # keys are lowcase
    '#c_a_k_e': 'eu',
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

USAGE = '/w (sender) !bgrank <type> [<region>]'
LINK = 'https://pubgtracker.com/api/profile/pc/{}'
API_KEY = '97d234e8-3d38-41ab-ba53-b5ef39ac7a95'
SEASON = '2017-pre2'
RESP = 'PUBG {type} {region}: Rank {Rank}, Rating {Rating}, Rounds {RoundsPlayed}, Wins {Wins}, Kills {Kills}, Top 10: {Top10s}'


def bgrank(self, args, msg):
    nick = bg_nick.get(msg.chan, None)
    if nick is None:
        return ''

    reg = default_type.get(msg.chan, 'na')  # region
    if args:
        if args[0].lower() in ('s', 'd', 'sq', 'solo', 'duo', 'squad'):
            type_ = args[0].lower()
        else:
            return USAGE

        if len(args) >= 2 and args[1].lower() in ('na', 'eu', 'as', 'sa', 'sea'):
            reg = args[1]
    else:
        type_ = 's'
    type_ = type_full.get(type_, type_)

    try:
        response = requests.get(LINK.format(nick),
                                headers={'TRN-Api-Key': API_KEY},
                                timeout=2.6).json()
        if 'error' in response:
            print(response.get('message', 'No message in response'))
            return None

        stats = next((x['Stats'] for x in response['Stats']
                      if x['Season'] == SEASON and x['Region'] == reg and x['Match'] == type_))
        stats_ = {x['field']: x['displayValue'] for x in stats}
        stats_.update(Rank=next(str(x['rank']) for x in stats if x['field'] == 'Rating'))

    except requests.RequestException:
        pp('Request exception (bgrank.py)', mtype='WARNING')
        return None
    except (KeyError, ValueError) as e:
        pp('{}: {} key is missing (bgrank.py)'.format(e.__class__.__name__, str(e)), mtype='WARNING')
        return None

    return RESP.format(type=type_.capitalize(), region=reg.upper(), **stats_)


''' OLD STUFF, parsing pubg.me
s = BeautifulSoup(page, 'html.parser')
a = s.select('div.profile-match-overview-solo div.profile-match-overview-header div.col-lg-10 div.col-md-4 div.stat div.value')
a = s.select('div.profile-match-overview-solo div.hidden-sm-down div.col-lg-10 div.col-md-4 div.stat div.value')'''


if __name__ == '__main__':
    class m: pass
    n = m(); n.chan = '#c_a_k_e'
    print(bgrank(None, ['solo'], n)); time.sleep(2)
    print(bgrank(None, ['DUO', 'na'], n)); time.sleep(2)
    print(bgrank(None, ['SQuad', 'eu'], n))

