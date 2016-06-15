#!/usr/bin/python
import json, urllib, sys, textwrap

from requests import auth
import requests

import pull, secrets


if len(sys.argv) == 3:
    repo_url, channel = sys.argv[1], sys.argv[2]
    testing = False
else:
    print '*** repo and/or channel not specified, running in debug mode ***'
    repo_url = 'https://api.github.com/repos/gigwalk-corp/gigwalk_apps_platform_api'
    channel = '#testing'
    testing = True

print 'repo_url:', repo_url
print 'channel:', channel

puller = pull.Puller(repo_url, testing)
user_dicts = puller.pull_recent()

max_chars = max(user_dict['total_chars'] for user_dict in user_dicts)
if max_chars == 0:
    max_chars = 1
max_bar_width = 40
bar_strs = []
for user_dict in user_dicts:
    norm_chars = user_dict['total_chars'] / float(max_chars)
    num_stars = int(round(norm_chars * max_bar_width))
    bar_strs.append('{}|{}({})'.format(
        user_dict['name'][:6], '*' * num_stars, user_dict['total_chars']))
bars_str = '```\n{}\n```'.format('\n'.join(bar_strs))

best_name = user_dicts[0]['name'] if user_dicts and user_dicts[0] else 'nobody'

print 'user_dicts:', user_dicts

slack_str = textwrap.dedent('''
    Code review scoreboard: {user_dicts}
    Good job {best_name}!
    Total characters typed:
    {bars_str}
    https://github.com/JesseAldridge/code_review_scoreboard
    ''').strip().format(
        user_dicts=user_dicts, bars_str=bars_str, best_name=best_name)

print 'slack_str:', slack_str

url = (
    'https://slack.com/api/chat.postMessage?token={}'
    '&channel={}&text={}&pretty=1').format(
    secrets.slack_api_key, urllib.quote(channel), urllib.quote(slack_str))
print 'url:', url
requests.post(url)
