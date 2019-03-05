# -*- coding: utf-8 -*-

config = {
    # details required to login to twitch IRC server
    'server': 'irc.chat.twitch.tv',
    'port': 6667,
    'username': '',
    'oauth_password': '',  # get this from http://twitchapps.com/tmi/
    'Client-ID': '',  # register an app in your twitch account settings
    'api_token': '',
    'api_version': 'application/vnd.twitchtv.v5+json',

    # maximum amount of bytes to receive from socket - 1024-4096 recommended
    'socket_buffer_size': 4096,

    # channels to join, lowcase, starts with '#'
    'channels': ['#xangold', '#twitchpresents']

}
