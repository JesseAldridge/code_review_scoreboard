import json, urllib

from requests import auth
import requests

import secrets

testing = False

username = 'JesseAldridge'
repo_url = 'https://api.github.com/repos/gigwalk-corp/gigwalk_apps_platform_api'


auth_ = auth.HTTPBasicAuth(username, secrets.github_api_key)
name_to_count = {}
for page in range(1, 3) if testing else range(1, 5):
    print 'page:', page

    main_resp = requests.get('{}/pulls?state=all&page={}'.format(repo_url, page), auth=auth_)
    all_prs = json.loads(main_resp.content)

    for pr in all_prs[:2] if testing else all_prs:
        created_by = pr['user']['login']
        print '  pr by:', created_by

        comments_resp = requests.get(pr['_links']['comments']['href'], auth=auth_)
        comments = json.loads(comments_resp.content)

        line_comments_resp = requests.get(pr['_links']['review_comments']['href'], auth=auth_)
        line_comments = json.loads(line_comments_resp.content)

        for comment in comments + line_comments:
            name = comment['user']['login']
            if name != created_by:
                print '    comment by:', name
                name_to_count.setdefault(name, 0)
                name_to_count[name] += 1

results = list(sorted(name_to_count.iteritems(), key=lambda t: -t[-1]))
print 'results:', results

slack_str = (
    'Code review scoreboard: {};  Good job {}!  '
    'https://github.com/JesseAldridge/code_review_scoreboard'.format(
        results, results[0][0] if results and results[0] else 'nobody'))

print 'slack_str:', urllib.quote(slack_str)

url = (
    'https://slack.com/api/chat.postMessage?token={}'
    '&channel=%23_eng_backend&text={}&pretty=1').format(
    secrets.slack_api_key, urllib.quote(slack_str))
requests.post(url)
