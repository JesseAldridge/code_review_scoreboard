import json
from datetime import datetime, timedelta

import requests
from requests import auth

import secrets

auth_ = auth.HTTPBasicAuth('JesseAldridge', secrets.github_api_key)


# Top-level comments(?)

since_str = (datetime.utcnow() - timedelta(days=14)).strftime('%Y-%m-%dT%H:%M:%SZ')

url = ('https://api.github.com/repos/gigwalk-corp/gigwalk_apps_platform_api/pulls/comments'
       '?sort=created&direction=desc&since={}&page={}').format(since_str, 1)

resp = requests.get(url, auth=auth_)
prs_list = json.loads(resp.content)

print prs_list[-1]['created_at']
# for pr_d in prs_list:
#   print pr_d['body']


# Inline comments(?)

since_str = (datetime.utcnow() - timedelta(days=14)).strftime('%Y-%m-%dT%H:%M:%SZ')

url = ('https://api.github.com/repos/gigwalk-corp/gigwalk_apps_platform_api/comments'
       '?sort=created&direction=desc&since={}&page={}').format(since_str, 1)

print 'url:', url

resp = requests.get(url, auth=auth_)
prs_list = json.loads(resp.content)

print prs_list[-1]['created_at']
for pr_d in prs_list:
  print pr_d['body']


# for page in range(1):
#   print page
#   # url = ('https://api.github.com/repos/gigwalk-corp/gigwalk_apps_platform_api/issues/comments'
#   #        '?sort=created&direction=desc&page={}').format(page)

#   # YYYY-MM-DDTHH:MM:SSZ

#   since_str = (datetime.utcnow() - timedelta(days=14)).strftime('%Y-%m-%dT%H:%M:%SZ')

#   url = ('https://api.github.com/repos/gigwalk-corp/gigwalk_apps_platform_api/pulls/comments'
#          '?sort=created&direction=desc&since={}&page={}').format(since_str, page)

#   resp = requests.get(url, auth=auth_)
#   prs_list = json.loads(resp.content)
#   if not prs_list:
#     print "that's all of them"
#     break
#   print prs_list[-1]['created_at']

#   print json.dumps(json.loads(resp.content), indent=2)
