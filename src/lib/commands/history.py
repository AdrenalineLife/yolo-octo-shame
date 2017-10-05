# -*- coding: utf-8 -*-
__author__ = 'Life'

from math import ceil

from src.lib.functions_general import pp


def history(self, args, msg):
    ch = next((x for x in self.ch_list if x.name == msg.chan[1:]), None)
    if ch is None:
        return ''
    with_time = True  # args and args[0] in ('t', 'time')

    # basic usage to show list of games
    if not args or args and args[0] in ('t', 'time'):
        result = ch.games_to_str(with_time)
        n = len(result) // 480
        games = [x.copy() for x in ch.games]
        chunk_size = ceil(len(games) / n)
        resp = []
        for games_slice in (games[i:i + n] for i in range(0, len(games), n)):
            resp.append(' → '.join(self.to_str_with_time(x) for x in games_slice))
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

