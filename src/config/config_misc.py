# coding: utf-8


config_misc = {
    # color of the bot in chat, name or #hex
    'color': 'Blue',

    # if True, colors will be used when printing messages, for Linux only i guess
    'use_logs_coloring': False,

    # if True, will display raw data received
    'debug': False,

    # if True, will log all messages from all channels
    # todo
    'log_messages': False,

    # if False, will not print chat messages
    'print_chat_msgs': True,

    # twitch has global limit of msg per 30 secs. 100 for mods, much more for known bots
    'global_msg_limit': 99,

    # how many chat messages to store for each channel
    'chat_messages_maxlen': 400,

    # list of IDs (str) of trusted users. Decide how you will use it yourself!
    'trusted_users': [],
}