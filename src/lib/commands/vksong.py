# -*- coding: utf-8 -*-
__author__ = 'Life'

import requests
import json

from src.res.authorization import *
from src.lib.functions_general import pp

groups = {
    '#c_a_k_e': '71257940',
    '#nastjadd': '67813745',
    '#adrenaline_life': '57857859',
    '#a_o_w': '57857859'
}


def vksong(self, args, msg):
    vk_id = groups.get('#adrenaline_life', None)
    if vk_id is None:
        return '/w (sender) Неизвестна группа vk для этого канала'

    vk_token = auth_vk_token
    vk_request = 'https://api.vk.com/method/status.get?group_id={}&access_token={}&v=5.92'
    try:
        status = requests.get(vk_request.format(vk_id, vk_token), timeout=2.6).json()
    except requests.RequestException:
        return 'Ошибка подключения'
    except ValueError as e:
        pp('ValueError: {} (vksong.py)'.format(str(e)), mtype='WARNING')
        return None

    #print(json.dumps(status, indent=4))

    try:
        response = status['response']
    except KeyError:
        pp("Code {}, {} (vksong.py)".format(status['error_code'], status['error_msg']), mtype='error')
        return ''
    if 'audio' not in response:
        return 'В данный момент музыка в vk не транслируется'
    else:
        seconds = response['audio']['duration']
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        print(m, s)
        timestr = '{:0>2}:{:0>2}:{:0>2}'.format(h, m, s) if h else '{0:0>2}:{1:0>2}'.format(m, s)
        return 'Сейчас играет: {artist} - {song}'.format(artist=response['audio']['artist'],
                                                         song=response['audio']['title'],
                                                         dur=timestr)


if __name__ == '__main__':
    print(vksong(None, [], None))