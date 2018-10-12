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
    resp = ''
    resp_kwargs = args.copy()
    if 'msg_param_months' not in resp_kwargs:
        resp_kwargs['msg_param_months'] = 0
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
                'amount': int(resp_kwargs['msg_param_mass_gift_count']),
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


a = [
{'badges': 'subscriber/3', 'color': '#1E90FF', 'display_name': 'alanmerf', 'emotes': '', 'flags': '', 'id': '574677eb-081b-482d-bef5-69a1aa4cea36',
 'login': 'alanmerf', 'mod': '0', 'msg_id': 'submysterygift', 'msg_param_mass_gift_count': '1', 'msg_param_sender_count': '12',
 'msg_param_sub_plan': '1000', 'room_id': '55935171', 'subscriber': '1',
 'system_msg': "alanmerf\\sis\\sgifting\\s1\\sTier\\s1\\sSubs\\sto\\sNastjadd's\\scommunity!\\sThey've\\sgifted\\sa\\stotal\\sof\\s12\\sin\\sthe\\schannel!",
 'tmi_sent_ts': '1538742840725', 'turbo': '0', 'user_id': '103295621', 'user_type': '', 'chan': '#c_a_k_e', 'msg': ''
},
{'badges': 'subscriber/3', 'color': '#1E90FF', 'display_name': 'alanmerf', 'emotes': '', 'flags': '', 'id': '6633025d-d7e7-44d5-b317-70e6a86fe90d',
 'login': 'alanmerf', 'mod': '0', 'msg_id': 'subgift', 'msg_param_months': '1', 'msg_param_recipient_display_name': '0qq_',
 'msg_param_recipient_id': '47010203', 'msg_param_recipient_user_name': '0qq_', 'msg_param_sender_count': '0',
 'msg_param_sub_plan_name':'Nastjadd\\s<3', 'msg_param_sub_plan': '1000', 'room_id': '55935171', 'subscriber': '1',
 'system_msg': 'alanmerf\\sgifted\\sa\\sTier\\s1\\ssub\\sto\\s0qq_!', 'tmi_sent_ts': '1538742841592', 'turbo': '0',
 'user_id': '103295621', 'user_type': '', 'chan': '#c_a_k_e', 'msg': ''},

{'badges': 'subscriber/12,sub-gifter/1', 'color': '#FA983A', 'display_name': 'Lanvilla', 'emotes': '', 'flags': '',
 'id': 'ac28c6e4-bb4d-491d-b8d8-4d1699113e77', 'login': 'lanvilla', 'mod': '0', 'msg_id': 'subgift',
 'msg_param_months': '1', 'msg_param_recipient_display_name': 'ppsrob', 'msg_param_recipient_id': '116879356',
 'msg_param_recipient_user_name': 'ppsrob', 'msg_param_sender_count': '0',
 'msg_param_sub_plan_name': 'Рядовая\\sподписка\\s\\s(c_a_k_e)', 'msg_param_sub_plan': '1000',
 'room_id': '43899589', 'subscriber': '1', 'system_msg': 'Lanvilla\\sgifted\\sa\\sTier\\s1\\ssub\\sto\\sppsrob!',
 'tmi_sent_ts': '1539275654877', 'turbo': '0', 'user_id': '38708525', 'user_type': '', 'chan': '#c_a_k_e',
 'msg': ''},
{'badges': 'subscriber/12,sub-gifter/1', 'color': '#FA983A', 'display_name': 'Lanvilla', 'emotes': '', 'flags': '',
 'id': '29b67752-bfd2-45d9-999f-e987c5308fc2', 'login': 'lanvilla', 'mod': '0', 'msg_id': 'subgift',
 'msg_param_months': '1', 'msg_param_recipient_display_name': 'dmitriymalikob',
 'msg_param_recipient_id': '182017873', 'msg_param_recipient_user_name': 'dmitriymalikob',
 'msg_param_sender_count': '0', 'msg_param_sub_plan_name': 'Рядовая\\sподписка\\s\\s(c_a_k_e)',
 'msg_param_sub_plan': '1000', 'room_id': '43899589', 'subscriber': '1',
 'system_msg': 'Lanvilla\\sgifted\\sa\\sTier\\s1\\ssub\\sto\\sdmitriymalikob!', 'tmi_sent_ts': '1539275654897',
 'turbo': '0', 'user_id': '38708525', 'user_type': '', 'chan': '#c_a_k_e', 'msg': ''},
{'badges': 'subscriber/12,sub-gifter/1', 'color': '#FA983A', 'display_name': 'Lanvilla', 'emotes': '', 'flags': '',
 'id': '22ee4497-2d24-45f7-8b71-a2961dbc02f4', 'login': 'lanvilla', 'mod': '0', 'msg_id': 'subgift',
 'msg_param_months': '1', 'msg_param_recipient_display_name': 'BavARetS', 'msg_param_recipient_id': '40646604',
 'msg_param_recipient_user_name': 'bavarets', 'msg_param_sender_count': '0',
 'msg_param_sub_plan_name': 'Рядовая\\sподписка\\s\\s(c_a_k_e)', 'msg_param_sub_plan': '1000',
 'room_id': '43899589', 'subscriber': '1', 'system_msg': 'Lanvilla\\sgifted\\sa\\sTier\\s1\\ssub\\sto\\sBavARetS!',
 'tmi_sent_ts': '1539275654933', 'turbo': '0', 'user_id': '38708525', 'user_type': '', 'chan': '#c_a_k_e',
 'msg': ''},
{'badges': 'subscriber/12,sub-gifter/1', 'color': '#FA983A', 'display_name': 'Lanvilla', 'emotes': '', 'flags': '',
 'id': '97f3a397-086d-409b-8e1a-4cd88ce3ea89', 'login': 'lanvilla', 'mod': '0', 'msg_id': 'subgift',
 'msg_param_months': '1', 'msg_param_recipient_display_name': 'marks_ds', 'msg_param_recipient_id': '239827875',
 'msg_param_recipient_user_name': 'marks_ds', 'msg_param_sender_count': '0',
 'msg_param_sub_plan_name': 'Рядовая\\sподписка\\s\\s(c_a_k_e)', 'msg_param_sub_plan': '1000',
 'room_id': '43899589', 'subscriber': '1', 'system_msg': 'Lanvilla\\sgifted\\sa\\sTier\\s1\\ssub\\sto\\smarks_ds!',
 'tmi_sent_ts': '1539275654958', 'turbo': '0', 'user_id': '38708525', 'user_type': '', 'chan': '#c_a_k_e',
 'msg': ''}]
for x in a:
    print(sub_greetings(None, x, None))