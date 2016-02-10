# -*- coding: utf-8 -*-

from random import randint

turned_on = {
    '#c_a_k_e': True,
    '#nastjanastja': True,
    '#adrenaline_life': True,
    '#a_o_w': True
}

allowed_users = ('a_o_w', 'adrenaline_life', 'c_a_k_e', 'nastjanastja')

# phrases should be in lower case
strip_phrases = (
    'вероятность что',
    'вероятность, что'
)


def m8(args, msg):
    if len(args) == 1 and args[0] in ('on', 'off'):
        if msg.name in allowed_users:
            turned_on[msg.chan] = True if args[0] == 'on' else False
        return ''

    if turned_on[msg.chan] or msg.name in allowed_users:
        check_string = ' '.join(args)
        lower_st = check_string.lower()
        for st in strip_phrases:
            if lower_st.startswith(st):
                check_string = check_string[len(st):]

        return msg.disp_name + ', вероятность, что {0} = {1}%'.format(check_string, randint(0, 101))
