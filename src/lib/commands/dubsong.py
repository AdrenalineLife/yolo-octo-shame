# -*- coding: utf-8 -*-
__author__ = 'Life'

import requests
import json

dub_rooms = {
    '#nastjanastja': 'nastjadds-party',
    '#meleeman777': 'meleeman'
}


def dubsong(self, args, msg):
    try:
        req = 'https://api.dubtrack.fm/room/{}'.format(dub_rooms[msg.chan])
    except KeyError:
        return 'Неизвестна комната для этого канала'

    try:
        resp = requests.get(req, timeout=6).json()
    except Exception:
        return 'Ошибочка...'

    #print(json.dumps(resp, indent=4))

    if resp['message'] != 'OK':
        return 'Ошибочка...'
    song = resp['data']['currentSong']
    return 'Сейчас играет на dubtrack: {}'.format(song['name']) if song is not None else 'Ничего не играет'


#print(dubsong(1, '#nastjanastja', 1))