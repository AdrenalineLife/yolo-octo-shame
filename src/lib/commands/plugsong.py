# -*- coding: utf-8 -*-
__author__ = 'Life'


import json

from urllib.parse import urljoin
from requests import Session
from re import search

from src.lib.functions_general import pp
from src.res.authorization import *


class PlugLoginError(Exception):
    pass


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
    csrf = js_var("_csrf", get_root.text)
    if csrf is None:
        raise PlugLoginError
    json_ = {"csrf": csrf, "email": email, "password": password}
    return post("auth/login", json=json_)


def join_room(room):
    return post("rooms/join", json={"slug": room})


def room_state():
    return get("rooms/state")


def name_of_user(uid):
    if uid is None:
        return ''
    resp = get('users/{}'.format(uid))
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

curr_room = ''
plug_rooms = {
    '#1': 'party-cake',
    '#2': 'i-the-80-s-and-90-s-1'
}


def plugsong(self, args, msg):
    global not_logged, plug_rooms, curr_room, session

    try:
        if not_logged:
            if login(mail, passw)['status'] != 'ok':  # logging and checking
                pp('Failed logging to PlugDJ', mtype='ERROR')
                return 'Ошибка подключения к PlugDJ'
            else:
                not_logged = False

        room_name = plug_rooms.get(msg.chan, None)
        if room_name is None:  # if plugdj room for this twitch chan is not provided
            return ''
        if curr_room != room_name:
            join_room(room_name)  # we should join a room before getting its state
            curr_room = room_name
        state = room_state()

    except PlugLoginError:
        not_logged = True
        session.cookies.clear()
        pp('Failed logging to PlugDJ: csrf is None', mtype='ERROR')
        return 'Ошибка подключения к PlugDJ'
    except Exception as detail:
        not_logged = True
        session.cookies.clear()
        pp('Failed logging to PlugDJ: {}'.format(detail), mtype='ERROR')
        return 'Ошибка подключения к PlugDJ'

    #print(json.dumps(state, sort_keys=True, indent=4))

    if state['status'] != 'ok':
        not_logged = True
        pp('Failed getting room state', mtype='ERROR')
        return 'Ошибка подключения к PlugDJ'
    else:
        state = state['data'][0]

    playback = state['playback']  # info about current song
    if playback:  # determining the form of the response
        if args and args[0] == 'room':
            resp = '{author} — {title} [{dur}]. DJ: {dj}. Людей: {ppl}. Очередь: {queue}. {url}'
        else:
            resp = 'Сейчас играет на {url} : {author} — {title} [{dur}]. DJ: {dj}'
    else:
        if args and args[0] == 'room':
            resp = 'Людей: {ppl}. Очередь: {queue}. {url}'
        else:
            return 'В данный момент музыка на PlugDJ не играет. {url}'

    if playback:  # if music is playing
        seconds = playback['media']['duration']
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        time_str = '{:0>2}:{:0>2}:{:0>2}'.format(h, m, s) if h else '{:0>2}:{:0>2}'.format(m, s)

        dj_id = state['booth']['currentDJ']
        dj_name = next((x['username'] for x in state['users'] if x['id'] == dj_id), None)
        dj_name = name_of_user(dj_id) if dj_name is None else dj_name

        return resp.format(author=playback['media']['author'],
                           title=playback['media']['title'],
                           dur=time_str,
                           dj=dj_name,
                           ppl=state['meta']['population'],
                           queue=len(state['booth']['waitingDJs']),
                           url='https://plug.dj/' + plug_rooms[msg.chan])

    else:
        return resp.format(ppl=state['meta']['population'],
                           queue=len(state['booth']['waitingDJs']),
                           url='plug.dj/' + plug_rooms[msg.chan])


if __name__ == '__main__':  # little bit of testing
    class MSG(object):  # fake message class
        pass
    msg_ = MSG()
    msg_.chan = '#1'

    print(plugsong(None, [], msg_))
    #print(plugsong(None, [], msg_)); time.sleep(2)
    #print(plugsong(None, [], msg_))
    print(plugsong(None, ['room'], msg_))
