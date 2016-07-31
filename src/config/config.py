# -*- coding: utf-8 -*-

config = {
    # details required to login to twitch IRC server
    'server': 'irc.chat.twitch.tv',
    'port': 6667,
    'username': '',
    'oauth_password': '',  # get this from http://twitchapps.com/tmi/
    'Client-ID': '',  # register an app in your twitch account settings

    # color of the bot in chat
    'color': 'Blue',

    # channels to join
    'channels': ['#chan1', '#chan2'],  # chan name starts with '#'

    # if set to true will display raw data received
    'debug': False,

    'cron': { #  CRON IS NOT SUPPORTED ATM
        '#channel_one': {
            'run_cron': False,
        # set this to false if you want don't want to run the cronjob but you want to preserve the messages etc
            'run_time': 100,  # time in seconds
            'cron_messages': [
                'This is channel_one cron message one.',
                'This is channel_one cron message two.'
            ]
        },

        '#channel_two': {
            'run_cron': False,
            'run_time': 20,
            'cron_messages': [
                'This is channel_two cron message one.'
            ]
        }
    },

    # if set to true will log all messages from all channels
    # todo
    'log_messages': False,

    # maximum amount of bytes to receive from socket - 1024-4096 recommended
    'socket_buffer_size': 4096  # 2048
}
