__author__ = 'Life'

import requests

import src.res.shorten_games as shorten_games
import src.res.uncover_names as uncover_names

from src.lib.functions_general import pp

LINK_FIND_USER = 'https://api.twitch.tv/kraken/users?login={}'
LINK_GET_STREAM = 'https://api.twitch.tv/kraken/streams/{}'


def check(self, args, msg):
    if not msg.is_mod:
        return ''
    if not args:
        return ''
    stream = uncover_names.uncover.get(args[0].lower().lstrip('@'), args[0])

    try:
        resp = requests.get(LINK_FIND_USER.format(stream), timeout=2.5, headers=self.req_headers).json()
        stream_id = resp['users'][0]['_id']  # now getting an ID !
        resp = requests.get(LINK_GET_STREAM.format(stream_id), timeout=2.5, headers=self.req_headers)
        if resp.status_code != 200:
            pp('check.py: status code is {} while getting stream'.format(resp.status_code), mtype='ERROR')
            return ''
        resp = resp.json()['stream']
    except (requests.RequestException, ValueError, KeyError, IndexError) as e:
        pp('check.py: while gettin stream, {}: {}'.format(e.__class__.__name__, str(e)), mtype='ERROR')
        return ''

    try:
        is_online = resp is not None
        if is_online:
            curr_game = resp['channel']['game']
            curr_game = shorten_games.shorten.get(curr_game, curr_game)
            viewers = resp['viewers']
            return 'Игра: {g}, Смотрит {v} на twitch.tv/{s}'.format(g=curr_game, v=viewers, s=stream)
        else:
            return 'Стрима нет ({})'.format(stream)
    except KeyError as e:
        pp('No "{}" key in api response (check.py)'.format(e), mtype='error')
        return ''
