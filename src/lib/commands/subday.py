# -*- coding: utf-8 -*-
__author__ = 'Life'

import requests
import time
import json

from src.lib.functions_general import pp

OPEN_RESP = 'Голосование открыто! %<название_игры> в чат {link} ({votes})'
CLOSE_RESP = 'Голосование закрыто! %<название_игры> в чат, когда откроется'

COOKIE = ''
LINK = 'https://servbot.khades.org/api/channel/{}/subdays/last'
RESULTS_PAGE = 'servbot.khades.org/#/channel/{}/subdays/last'

'''
def subday_(self, args, msg):
    link = LINK_BASE + '/events/get/{}/subday'.format(msg.chan[1:])
    try:
        resp = requests.get(link, timeout=4.0, headers={
            'Cookie': COOKIE
        })

        link = LINK_BASE + resp.json()['redirect']
        resp = requests.get(link, timeout=4.0, headers={
            'Cookie': COOKIE
        })
        data = resp.json()['event']
        #print(json.dumps(resp.json(), indent=4))
        is_opened = 'dtend' not in data
        votes = len(data.get('votes', []))
        results_page = 'vote.khades.org/#/events/{}/subday'.format(msg.chan[1:])
        #print(resp.text, resp.status_code, '\n', is_opened)
        resp_str = OPEN_RESP if is_opened else CLOSE_RESP
    except (requests.RequestException, ValueError, KeyError) as e:
        pp("subday.py, {}: {}".format(e.__class__.__name__, str(e)), mtype='ERROR')
        return
    return resp_str.format(votes=votes, link=results_page)
'''


def subday(self, args, msg):
    link = LINK.format(msg.chan_id)
    try:
        resp = requests.get(link, timeout=2.5, headers={
            'Cookie': COOKIE,
            'Accept': 'application/json, text/*'
        })
        if resp.status_code != 200:
            pp("subday.py, status code is {}".format(resp.status_code), mtype='ERROR')
        data = resp.json()
        #print(json.dumps(data, indent=4), '\n')
        is_opened = data['isActive']
        votes = len(data.get('votes', []))
        results_page = RESULTS_PAGE.format(msg.chan_id)
        #print(resp.status_code, '\n', is_opened)
        resp_str = OPEN_RESP if is_opened else CLOSE_RESP
    except (requests.RequestException, ValueError, KeyError) as e:
        pp("subday.py, {}: {}".format(e.__class__.__name__, str(e)), mtype='ERROR')
        return
    return resp_str.format(votes=votes, link=results_page)


if __name__ == '__main__':
    class MSG(object):  # fake message class
        pass
    msg_ = MSG()
    msg_.chan_id = '43899589'

    print(subday(None, None, msg_))
