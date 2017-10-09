# -*- coding: utf-8 -*-
__author__ = 'Life'

import requests
import datetime

import src.config.config as cfg
from src.lib.functions_general import pp

turned_on = {x: False for x in cfg.config['channels']}
ALLOWED_USERS = (85413884,)


def followtime(self, args, msg):
    if args and args[0] in ('on', 'off'):
        if msg.is_mod or msg.user_id in ALLOWED_USERS:
            turned_on[msg.chan] = True if args[0] == 'on' else False
        return ''

    if turned_on[msg.chan] or msg.is_mod:
        now = datetime.datetime.utcnow()
        link = 'https://api.twitch.tv/kraken/users/{}/follows/channels/{}'
        try:
            resp = requests.get(link.format(msg.user_id, msg.chan_id), headers=self.req_headers, timeout=3.2).json()
        except (requests.RequestException, ValueError):
            pp('Error while making request (followtime.py)', mtype='error')
            return
        if 'error' in resp:
            return
        created_at = resp['created_at'].split('+')[0]
        days = (now - datetime.datetime.strptime(created_at, '%Y-%m-%dT%H:%M:%SZ')).days
        years, days = divmod(days, 365)
        month, days = divmod(days, 30)
        if years:
            resp_string = '{y} г {m} м {d} д'
        elif month:
            resp_string = '{m} м {d} д'
        else:
            resp_string = '{d} дней'

        return '(sender) фолловит ' + resp_string.format(y=years, m=month, d=days)
