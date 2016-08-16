#!/usr/bin/python
import json, urllib, sys, textwrap, os, codecs
from datetime import datetime

from requests import auth
import requests

import _0_pull, secrets

# Parse command line params or use testing defaults.

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

# Pull recent comments.

puller = _0_pull.Puller(repo_url, testing)
users_by_score = puller.pull_recent()

print 'users_by_score:', users_by_score

repo_name = '_'.join(repo_url.split('/')[-2:])
timestamp_str = '{}'.format(
    datetime.utcnow()).replace(' ', '_').replace(':', '-').replace('.', '-')
report_name = '{}/{}'.format(repo_name, timestamp_str)

repo_path = os.path.join('reports', repo_name)
if not os.path.exists(repo_path):
    os.makedirs(repo_path)
out_text = json.dumps([user.to_full_report_dict() for user in users_by_score])
with codecs.open('reports/{}'.format(report_name), mode='w', encoding='utf8') as f:
    f.write(out_text)

# Generate bars.

max_chars = max(user.get_total_chars() for user in users_by_score)
if max_chars == 0:
    max_chars = 1
max_bar_width = 40
bar_strs = []
for user in users_by_score:
    norm_chars = user.get_total_chars() / float(max_chars)
    num_stars = int(round(norm_chars * max_bar_width))
    bar_strs.append('{}|{}({})'.format(
        user.name[:6], '*' * num_stars, user.get_total_chars()))
bars_str = '```\n{}\n```'.format('\n'.join(bar_strs))

# Generate slack string.

best_name = users_by_score[0].name if users_by_score else 'nobody'
user_dicts = [user.to_slack_dict() for user in users_by_score]

slack_str = textwrap.dedent('''
    Code review scoreboard: {user_dicts}
    Good job {best_name}!
    Total characters typed:
    {bars_str}
    Full report:  http://54.183.41.231/{report_name}
      Username:  {server_username}  Password:  {server_password}
    GitHub repo:  https://github.com/JesseAldridge/code_review_scoreboard
    ''').strip().format(
        user_dicts=user_dicts, bars_str=bars_str, best_name=best_name, report_name=report_name,
        server_username=secrets.server_username, server_password=secrets.server_password)
print 'slack_str:', slack_str

# Post to slack.

url = (
    'https://slack.com/api/chat.postMessage?token={}'
    '&channel={}&text={}&pretty=1').format(
    secrets.slack_api_key, urllib.quote(channel), urllib.quote(slack_str))
print 'url:', url
requests.post(url)
