import json
from datetime import datetime, timedelta

import requests
from requests import auth

import secrets

auth_ = auth.HTTPBasicAuth('JesseAldridge', secrets.github_api_key)

for page in range(20):
  print page
  # url = ('https://api.github.com/repos/gigwalk-corp/gigwalk_apps_platform_api/issues/comments'
  #        '?sort=created&direction=desc&page={}').format(page)

  # YYYY-MM-DDTHH:MM:SSZ

  since_str = (datetime.utcnow() - timedelta(days=14)).strftime('%Y-%m-%dT%H:%M:%SZ')

  url = ('https://api.github.com/repos/gigwalk-corp/gigwalk_apps_platform_api/pulls/comments'
         '?sort=created&direction=desc&since={}&page={}').format(since_str, page)

  resp = requests.get(url, auth=auth_)
  prs_list = json.loads(resp.content)
  if not prs_list:
    print "that's all of them"
    break
  print prs_list[-1]['created_at']

  json.dumps(json.loads(resp.content), indent=2)
  if 'Do we want some kind of error reporting' in resp.content:
    print 'found it'

