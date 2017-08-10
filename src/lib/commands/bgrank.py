# -*- coding: utf-8 -*-
__author__ = 'Life'

import requests
import json
import time

from src.lib.functions_general import pp

bg_nick = {  # PUBG nickname
    '#c_a_k_e': 'CakeDestroyer',
    '#': ''
}

# default region for the channel
default_reg = {  # keys are lowcase
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
API_KEY = ''
RESP = 'PUBG {type} {region}: Rank {Rank}, Rating {Rating}, Rounds {RoundsPlayed}, Wins {Wins}, Kills {Kills}, Top 10: {Top10s}'


def bgrank(self, args, msg):
    nick = bg_nick.get(msg.chan, None)
    if nick is None:
        pp('No PUBG nickname found for channel {}'.format(msg.chan), mtype='WARNING')
        return ''

    reg = default_reg.get(msg.chan, 'na')  # region
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
                                timeout=2.4).json()

        if 'error' in response:
            pp('Error in response: {} (bgrank.py)'.format(
                response.get('message', response.get('error', 'No message'))), mtype='WARNING')
            return None

        season = response['defaultSeason']  # rename it carefull, used later through locals().get()
        stats = next((x['Stats'] for x in response['Stats']  # all stats for curr season, region and type
                      if x['Season'] == season and x['Region'] == reg and x['Match'] == type_))
        stats_ = {x['field']: x['value'] for x in stats}
        stats_.update(Rank=next(str(x['rank']) for x in stats if x['field'] == 'Rating'))

    except requests.Timeout:
        pp('Request timeout (bgrank.py)', mtype='WARNING')
        return None
    except requests.RequestException as e:
        pp('{}: {} (bgrank.py)'.format(e.__class__.__name__, str(e)[:70]), mtype='WARNING')
        return None
    except KeyError as e:
        pp('KeyError: {} key is missing (bgrank.py)'.format(str(e)), mtype='WARNING')
        return None
    except ValueError as e:
        pp('ValueError: {} (bgrank.py)'.format(str(e)), mtype='WARNING')
        return None
    except StopIteration:
        return 'Не найдено игр на {type} {region} {season}'.format(type=type_.capitalize(),
                                                                   region=reg.upper(),
                                                                   season=locals().get('season', ''))  # tricky

    return RESP.format(type=type_.capitalize(), region=reg.upper(), **stats_)


''' OLD STUFF, parsing pubg.me
s = BeautifulSoup(page, 'html.parser')
a = s.select('div.profile-match-overview-solo div.profile-match-overview-header div.col-lg-10 div.col-md-4 div.stat div.value')
a = s.select('div.profile-match-overview-solo div.hidden-sm-down div.col-lg-10 div.col-md-4 div.stat div.value')'''


if __name__ == '__main__':
    class m: pass
    n = m(); n.chan = '#c_a_k_e'
    print(bgrank(None, ['solo'], n)); time.sleep(2)
    print(bgrank(None, ['duo'], n)); time.sleep(2)
    print(bgrank(None, ['DUO', 'na'], n)); time.sleep(2)
    #print(bgrank(None, ['SQuad', 'eu'], n))

