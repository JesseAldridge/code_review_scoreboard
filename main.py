#!/usr/bin/python
import json, urllib

from requests import auth
import requests

import pull, secrets

testing = False

# repo_url = 'https://api.github.com/repos/gigwalk-corp/gigwalk_apps_platform_api'
# channel = '#_eng_backend'

repo_url = 'https://api.github.com/repos/gigwalk-corp/gigwalk_apps_platform'
channel = '#eng'

puller = pull.Puller(repo_url, testing)
results = puller.pull_recent()

slack_str = (
    'Code review scoreboard: {};  Good job {}!  '
    'https://github.com/JesseAldridge/code_review_scoreboard'.format(
        results, results[0][0] if results and results[0] else 'nobody'))

print 'slack_str:', slack_str

url = (
    'https://slack.com/api/chat.postMessage?token={}'
    '&channel={}&text={}&pretty=1').format(
    secrets.slack_api_key, urllib.quote(channel), urllib.quote(slack_str))
print 'url:', url
requests.post(url)
