# -*- coding: utf-8 -*-
__author__ = 'Life'

import requests
import json

err = '¯\(ツ)/¯'


def dubsong(args, chan, username):
    if chan in ('#nastjanastja', '#a_o_w'):
        req = 'https://api.dubtrack.fm/room/nastjadds-party'
        try:
            resp = requests.get(req).json()
        except Exception:
            return err

        #print(json.dumps(resp, indent=4))

        if resp['message'] != 'OK':
            return err
        else:
            return 'Сейчас играет на dubtrack: %s' % resp['data']['currentSong']['name']
    else:
        return ''

#dubsong(1, '#nastjanastja', 1)