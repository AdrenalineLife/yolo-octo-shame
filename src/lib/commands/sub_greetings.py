# -*- coding: utf-8 -*-
__author__ = 'Life'


from src.res.sub_greetings_phrases import greetings
from src.lib.functions_general import pp

for x in greetings:
    if 'emote' not in greetings[x]:
        greetings[x]['emote'] = ''

RENAME = (('msg_param_months', 'm'),
          ('msg_param_sub_plan', 'plan'),)

mysteries = {}  # mystery gifts


def sub_greetings(self, args, msg):
    resp_kwargs = args.copy()
    for old, new in RENAME:
        resp_kwargs[new] = resp_kwargs[old]
    chan_greets = greetings.get(resp_kwargs['chan'], None)
    if chan_greets is None:  # TODO notify as an option
        return ''

    resp_kwargs['m'] = 0 if resp_kwargs['m'] == '1' else int(resp_kwargs['m'])
    if resp_kwargs['msg_id'] == 'subgift':
        resp_kwargs['givenby'] = resp_kwargs['login'].replace(r'\s', '')
        resp_kwargs['login'] = resp_kwargs['msg_param_recipient_user_name'].replace(r'\s', '')

    try:
        if resp_kwargs['msg_id'] == 'subgift':  # in case of subgift
            if resp_kwargs['chan'] not in mysteries:
                mysteries[resp_kwargs['chan']] = {}
            myst = mysteries[resp_kwargs['chan']].get(resp_kwargs['user_id'], None)
            if myst is not None:
                myst['recipients'].append(resp_kwargs['msg_param_recipient_user_name'])

                if len(myst['recipients']) >= myst['amount']:
                    resp_kwargs['recipients_list'] = ', '.join(myst['recipients'])
                    resp_kwargs['msg_param_mass_gift_count'] = myst['amount']
                    resp = chan_greets['mysterygifts_recipients']
                    mysteries[resp_kwargs['chan']].pop(resp_kwargs['user_id'])

            else:
                total_ = chan_greets.get('gifted_total', '') if resp_kwargs['msg_param_sender_count'] != '0' else ''
                resp = '{} {}'.format(chan_greets['gift'], total_)

        elif resp_kwargs['msg_id'] == 'submysterygift':
            #resp = chan_greets.get('submysterygift', '')
            if resp_kwargs['chan'] not in mysteries:
                mysteries[resp_kwargs['chan']] = {}
            mysteries[resp_kwargs['chan']][resp_kwargs['user_id']] = {
                'amount': resp_kwargs['msg_param_mass_gift_count'],
                'recipients': []
            }

        else:
            if not resp_kwargs['plan'].lower() == 'prime':
                resp = chan_greets['resub'] if resp_kwargs['m'] else chan_greets['new']
            else:
                resp = chan_greets['resub_p'] if resp_kwargs['m'] else chan_greets['new_p']
        emote = chan_greets['emote'].strip() + ' '
        resp_kwargs['e'] = emote

    except KeyError as e:
        pp('No key found: {} (sub_greetings.py)'.format(e), mtype='ERROR')
        return ''

    try:
        return resp.format(**resp_kwargs)
    except KeyError as e:
        pp('No key found while formatting: {} (sub_greetings.py)'.format(e), mtype='ERROR')
        return ''
