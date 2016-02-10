# -*- coding: utf-8 -*-
__author__ = 'Life'
import requests
from src.res.authorization import *
import json

groups = {
    '#c_a_k_e': '71257940',
    '#nastjanastja': '67813745',
    '#adrenaline_life': '67813745',
    '#a_o_w': '57857859'
}


def vksong(args, msg):
    try:
        vk_id = groups[msg.chan]
    except KeyError:
        return 'Неизвестна группа vk для этого канала'
    vk_token = auth_vk_token
    vk_request = 'https://api.vk.com/method/status.get?group_id=%s&access_token=%s' % (vk_id, vk_token)
    try:
        status = requests.get(vk_request, timeout=3).json()
    except Exception:
        return 'Ошибка подключения'

    #print(json.dumps(status, indent=4))
    if 'audio' not in status['response']:
        return 'В данный момент музыка в vk не транслируется'
    else:
        seconds = status['response']['audio']['duration']
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        timestr = '%02d:%02d:%02d' % (h, m, s) if h else '%02d:%02d' % (m, s)
        return 'Сейчас играет: %s - %s [%s]' % (status['response']['audio']['artist'],
                                                status['response']['audio']['title'],
                                                timestr)

#print(vksong([], '#c_a_k_e', 'username'))