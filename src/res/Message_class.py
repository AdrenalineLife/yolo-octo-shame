# -*- coding: utf-8 -*-
__author__ = 'Life'


zalgo_chars = ('͑','͚','̧','͌','̈́','̈','̓','̉','͂','͙','͘','̦','͉','̍','͗','̃','̽','̩','͇','̭','̠','́','̟','̮','͡','͝',
               '̣','̹','ͩ','̼','̬','ͅ','͔','͆','̕','ͤ','̖','̶','͕','҉','ͣ','̛','̌','̙','̾','̓','͟','ͥ','͞','̞','ͮ','̥',
               '̋','̐','̨','̷','ͧ','ͪ','̄','͛','̝','͜','̒','̰','ͭ','̜','̲','̅','́','͠','̵','͢','̆','̀','̳','̢','̘','̀',
               '̗','͖','̔','̯','̚','ͬ','̂','̺','͈','̿','̎','̏','̊','͓','ͫ','ͨ','ͯ','̱','̡','ͦ','͋','͒','̫','̤','̻','̴',
               '͐','̇','͏','͍','͊','̸','͎','̑','̪')


class Message(object):
    def __init__(self, name, disp, msg, chan, color='', is_sub='0', is_mod='0', is_turbo='0', m_id=''):
        self.name = name.replace('\s', '')
        self.disp_name = disp.replace('\s', '') if disp else self.name
        self.message = msg
        self.chan = chan
        self.color = color
        self.is_mod = is_mod == '1' or self.name == self.chan[1:]
        self.is_sub = is_sub == '1'
        self.is_turbo = is_turbo == '1'
        self.msg_id = m_id

    def is_zalgo(self, threshold=40):
        if len(self.message) < threshold:
            return False
        cnt = 0
        for char in self.message:
            if char in zalgo_chars:
                cnt += 1
            if cnt >= threshold:
                return True
        return False

    def __repr__(self):
        return '[s:{x.is_sub}, m:{x.is_mod}, t:{x.is_turbo} {x.chan}] <{x.disp_name}> {x.message}'.format(x=self)
