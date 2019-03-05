# -*- coding: utf-8 -*-

config = {
    # details required to login to twitch IRC server
    'server': 'irc.chat.twitch.tv',
    'port': 6667,
    'username': 'Adrenaline_Life',
    'oauth_password': 'oauth:iyprc9k2p0cofr40t611vusirp2g5t',  # get this from http://twitchapps.com/tmi/
    'Client-ID': 'rplsl1y05kzxaegno8q2jvhgicco5kh',  # register an app in your twitch account settings
    'api_token': 'OAuth zj9mn5tnryavzew39sx1tkw1c76ojo',

    #oauth:chu05sxlp6bupjrjsurjn8vb1n0fpv
    #80rpzihvfvrtcj9x7w0ac0wzgg668zg
    #OAuth 8oukuo9mtu28arn204a190tiv6ht3g

    # color of the bot in chat
    'color': 'Blue',

    # channels to join
    'channels': ['#adrenaline_life', '#a_o_w', '#nastjadd', #'#gn_gg', '#kvyzee', '#dakotaz', '#thijs', '#playoverwatch_kr',
                 '#twitchpresents'],  # chan name starts with '#'

    # if set to true will display raw data received
    'debug': False,

    'cron': {  # CRON IS NOT SUPPORTED ATM
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
