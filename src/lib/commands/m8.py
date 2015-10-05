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
    'вероятность, что',
)


def m8(args, chan, username):
    if len(args) == 1 and args[0] in ('on', 'off'):
        if username in allowed_users:
            turned_on[chan] = True if args[0] == 'on' else False
        return ''

    if turned_on[chan] or username in allowed_users:
        check_string = ' '.join(args)
        lower_st = check_string.lower()
        for st in strip_phrases:
            if lower_st.startswith(st):
                check_string = check_string[len(st):]

        return 'вероятность, что {0} = {1}%'.format(check_string, randint(0, 101))


if __name__ == '__main__':
    phrases = (
        'Вероятность, что аов бот',
        'вероЯТность что мама мыла раму',
        'дота очень интересная игра'
    )

    for st in phrases:
        print(m8(st.split(' '), '#c_a_k_e', 'adrenaline_life'))