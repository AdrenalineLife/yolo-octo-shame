# -*- coding: utf-8 -*-
__author__ = 'Life'

from math import ceil

from src.lib.functions_general import pp


def history(self, args, msg):
    ch = next((x for x in self.ch_list if x.name == msg.chan[1:]), None)
    if ch is None:
        return ''
    with_time = True  # args and args[0] in ('t', 'time')
    sep = ' → '

    # basic usage to show list of games
    if not args or args and args[0] in ('t', 'time'):
        if not ch.games:
            return 'Список игр пуст'
        result = ch.games_to_str(with_time, separator=sep)
        n = ceil(len(result.encode()) / 499s)
        result = result.split(sep)
        chunk_size = ceil(len(result) / n)
        resp = []
        for games_slice in (result[i:i + chunk_size] for i in range(0, len(result), chunk_size)):
            resp.append(sep.join(x for x in games_slice))
        return resp

    # advanced usage to manage list of games
    if args and args[0] in ('clear', 'del'):
        if msg.is_mod or msg.name == 'adrenaline_life':
            if args[0] == 'clear':
                ch.clear_games_list()
                return 'Список игр был очищен'
            elif args[0] == 'del' and len(args) == 2:
                try:
                    ch.del_game(int(args[1]))
                    return ''
                except ValueError:
                    pp("history: не удалось преобразовать '{}' в целое число".format(args[1]), mtype='ERROR')
                    return ''
                except IndexError:
                    pp("history: неверный индекс '{}' (нумерация начинается с нуля)".format(args[1]), mtype='ERROR')
                    return ''

