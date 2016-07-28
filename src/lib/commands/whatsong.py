# -*- coding: utf-8 -*-
__author__ = 'Life'

import requests
import time
import re

headers = {'X-Requested-With': 'XMLHttpRequest'}


def whatsong(self, args, msg):
    global headers
    site_base = 'http://www.twitchecho.com/'

    if not self.cmd_headers['!whatsong']['activated']:
        try:
            r = requests.get(site_base, headers=headers, timeout=4)
            headers['Cookie'] = r.headers['set-cookie'].split(';')[0]  # getting our cookies

            link = site_base + 'welcome/listen?utf8=%E2%9C%93&stream=' + msg.chan[1:]
            r = requests.get(link, headers=headers, timeout=4)
            headers['Cookie'] = r.headers['set-cookie'].split(';')[0]

            self.cmd_headers['!whatsong']['activated'] = True
            self.cmd_headers['!whatsong']['time'] = time.time()
            self.cmd_headers['!whatsong']['req_chan'] = msg.chan
            self.cmd_headers['!whatsong']['req_name'] = msg.disp_name

            return '/w (sender) Определяем музыку...'
        except Exception:
            headers.pop('Cookie', None)
            return ''
    elif args and args[0] == 'chk':
        try:
            r = requests.get(site_base + 'welcome/update_result?stream=' + self.cmd_headers['!whatsong']['req_chan'][1:],
                             headers=headers, timeout=4)
            if 'Title:' in r.text and 'Artist:' in r.text:
                artist = re.search('Artist: (.*)\n', r.text).group(1)
                title = re.search('Title: (.*)\n', r.text).group(1)
                return ["Скорее всего играет '{} - {}'".format(artist, title),
                        '/w (sender) {} - {}'.format(artist, title)]
            elif "couldn't find a match!" in r.text:
                return 'Не удалосъ распознать музыку'
            else:
                return ''
        except Exception:
            return ''  # todo