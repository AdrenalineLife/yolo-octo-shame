# -*- coding: utf-8 -*-
__author__ = 'Life'

import requests
import json

err = 'Ошибочка...' #'¯\(ツ)/¯'


def dubsong(args, chan, username):
    if chan in ('#nastjanastja', '#a_o_w'):
        req = 'https://api.dubtrack.fm/room/nastjadds-party'
        try:
            resp = requests.get(req).json()
        except Exception:
            return err

        print(json.dumps(resp, indent=4))

        if resp['message'] != 'OK':
            return err
        song = resp['data']['currentSong']
        return 'Сейчас играет на dubtrack: %s' % song['name'] if song is not None else 'Ничего не играет'
    else:
        return ''

#print(dubsong(1, '#nastjanastja', 1))