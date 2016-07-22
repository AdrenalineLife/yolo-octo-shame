# -*- coding: utf-8 -*-
__author__ = 'Life'

'''
PLEASE NOTE:
http://plug.dj has been shut down
due to inability to pay for hosting
'''


import json
from urllib.parse import urljoin
from requests import Session
from re import search

from src.lib.functions_general import pp
from src.res.authorization import *

class LoginError(Exception): pass

def js_var(var, raw):
    """ really hacky-hack helper to extract js str var decls. """
    lestr = r"\b{0}\s*=\s*\"([^\"]+)".format(var)
    match = search(lestr, raw)
    return None if match is None else match.group(1)

def to_url(endpoint):
    return urljoin(rest_url_base, "/_/" + endpoint)

def post(path, return_req=False, **kwargs):
    req = session.post(to_url(path), **kwargs)
    if return_req:
        return req
    return req.json()

def get(path, return_req=False, **kwargs):
    req = session.get(to_url(path), **kwargs)
    if return_req:
        return req
    return req.json()

def login(email, password):
    get_root = session.get(urljoin(rest_url_base, "/"))
    resp = get_root.text
    csrf = js_var("_csrf", resp)
    if csrf is None:
        raise LoginError
    json = {"csrf": csrf, "email": email, "password": password}
    return post("auth/login", json=json)

def join_room(room):
    return post("rooms/join", json={"slug": room})

def room_state():
    return get("rooms/state")

def name_of_user(uid):
    if uid is None:
        return ''
    resp = get('users/%s' % uid)
    if resp['status'] != 'ok':
        return ''
    else:
        return resp['data'][0]['username']

rest_url_base = "https://plug.dj"
session = Session()
session.headers.update({"User-Agent": "plugAPI_3.2.1"})
mail = auth_plug_login
passw = auth_plug_pass

not_logged = True


def plugsong(self, args, chan):
    global not_logged
    try:
        if not_logged:
            if login(mail, passw)['status'] != 'ok':
                pp('Failed logging to PlugDJ', 'ERROR')
                return 'Ошибка подключения к PlugDJ'
            else:
                not_logged = False
            join_room('nastjadd')
        state = room_state()
    except LoginError:
        not_logged = True
        pp('Failed logging to PlugDJ: csrf is None', 'ERROR')
        return 'Ошибка подключения к PlugDJ'
    except Exception as detail:
        not_logged = True
        pp('Failed logging to PlugDJ: %s' % detail, 'ERROR')
        return 'Ошибка подключения к PlugDJ'

    #print(json.dumps(state, sort_keys=True, indent=4, separators=(',', ': ')))

    if state['status'] != 'ok':
        not_logged = True
        pp('Failed getting room state', 'ERROR')
        return 'Ошибка подключения к PlugDJ'

    if state['data'][0]['playback']:
        seconds = state['data'][0]['playback']['media']['duration']
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        timestr = '%02d:%02d:%02d' % (h, m, s) if h else '%02d:%02d' % (m, s)
        resp = 'Сейчас играет на PlugDJ: %s - %s [%s]' % (state['data'][0]['playback']['media']['author'],
                                                          state['data'][0]['playback']['media']['title'],
                                                          timestr)
        djname = name_of_user(state['data'][0]['booth']['currentDJ'])
        if djname: resp += '. DJ: %s' % djname
        return resp
    else:
        return 'В данный момент музыка на PlugDJ не играет'

#plugsong(None, [], 'channel')