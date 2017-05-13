# -*- coding: utf-8 -*-
__author__ = 'Life'

import re


def banall(self, args, msg):
    try:
        if msg.is_mod:
            regex = ' '.join(args)
            r = re.compile(regex, flags=re.IGNORECASE)
            res = list({'/timeout {} {}'.format(x.name, 32) for x in self.chat_messages[msg.chan]
                        if r.search(x.message)})[:70]
            return res
    except Exception:
        return ''

if __name__ == '__main__':
    pass