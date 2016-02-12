#!/usr/bin/python
import json, urllib, os
from datetime import datetime
import logging

from requests import auth
import requests

import secrets

logging.basicConfig(filename=os.path.expanduser("~/all_prs.log"), level=logging.DEBUG)
logger = logging.getLogger('all_prs')

class Puller:
    def __init__(self, repo_url, testing):
        self.repo_url = repo_url
        self.testing = testing

        username = 'JesseAldridge'

        self.auth_ = auth.HTTPBasicAuth(username, secrets.github_api_key)
        self.name_to_count = {}

    def pull_page(self, page):
        print 'page:', page

        main_resp = requests.get('{}/pulls?state=all&page={}'.format(
            self.repo_url, page), auth=self.auth_)
        all_prs = json.loads(main_resp.content)

        logger.debug('all_prs: {}'.format(json.dumps(all_prs, indent=2)))

        for pr in all_prs[:2] if self.testing else all_prs:

            created_by = pr['user']['login']
            print '  pr {} by: {}'.format(pr['_links']['self'], created_by)

            full_pr_resp = requests.get(pr['_links']['self']['href'], auth=self.auth_)
            full_pr = json.loads(full_pr_resp.content)
            if full_pr['merged_by']:
                name = full_pr['merged_by']['login']
                if name != created_by:
                    print '    merged_by:', name
                    self.increment(name)

            comments_resp = requests.get(pr['_links']['comments']['href'], auth=self.auth_)
            comments = json.loads(comments_resp.content)

            line_comments_resp = requests.get(
                pr['_links']['review_comments']['href'], auth=self.auth_)
            line_comments = json.loads(line_comments_resp.content)

            for comment in comments + line_comments:
                name = comment['user']['login']
                if name != created_by:
                    print '    comment by:', name
                    self.increment(name)

    def pull_recent(self):
        for page in range(1, 3) if self.testing else range(1, 5):
            self.pull_page(page)

        results = list(sorted(self.name_to_count.iteritems(), key=lambda t: -t[-1]))
        print 'results:', results
        return results

    def increment(self, name):
        self.name_to_count.setdefault(name, 0)
        self.name_to_count[name] += 1

if __name__ == '__main__':
    testing = False

    puller = Puller('https://api.github.com/repos/gigwalk-corp/gigwalk_apps_platform_api', testing)

    # puller.pull_page(3)

    results = puller.pull_recent()
    with open('results.txt', 'a') as f:
        f.write('{} {}\n'.format(datetime.now(), results))
