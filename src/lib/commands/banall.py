# -*- coding: utf-8 -*-
__author__ = 'Life'

import re
from math import ceil
from src.lib.functions_general import pp


def banall(self, args, msg):
    try:
        bantime = 50
        if msg.is_mod:
            try:
                bantime = abs(float(args[0]))
            except ValueError:
                return 'Укажите время бана в минутах первым аргументом'
            bantime = ceil(bantime*60)
            regex = ' '.join(args[1:])
            r = re.compile(regex, flags=re.IGNORECASE)
            res = list({'/timeout {} {}'.format(x.name, bantime) for x in self.chat_messages[msg.chan]
                        if r.search(x.message)})[:70]
            return res

    except re.error as e:
        pp('{} (banall.py)'.format(e), mtype='error')
        return ''
    except Exception:
        return ''


if __name__ == '__main__':
    pass