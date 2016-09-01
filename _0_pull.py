#!/usr/bin/python
import json, urllib, os, sys
from datetime import datetime
import logging

from requests import auth
import requests

import secrets

logging.basicConfig(filename=os.path.expanduser("~/all_prs.log"), level=logging.DEBUG)
logger = logging.getLogger('all_prs')
logger.debug("beginning run at {}".format(datetime.now()))


class User:
    def __init__(self, name):
        self.name = name
        self.score = 0
        self.merges = 0
        self.comments = []

    def to_slack_dict(self):
        return {"name": self.name, "score": self.score, "total_chars": self.get_total_chars()}

    def to_full_report_dict(self):
        return {"name": self.name, "score": self.score, "comments": self.comments}

    def get_total_chars(self):
        return sum((len(comment['body']) for comment in self.comments))


class Puller:
    def __init__(self, repo_url, testing):
        self.repo_url = repo_url
        self.testing = testing

        username = 'JesseAldridge'

        self.auth_ = auth.HTTPBasicAuth(username, secrets.github_api_key)
        self.name_to_user = {}

    def pull_page(self, page):
        # Fill up the name_to_user dict with all comments on the page.

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
                    self.name_to_user[name].merges += 1

            comments_resp = requests.get(pr['_links']['comments']['href'], auth=self.auth_)
            comments = json.loads(comments_resp.content)

            line_comments_resp = requests.get(
                pr['_links']['review_comments']['href'], auth=self.auth_)
            line_comments = json.loads(line_comments_resp.content)

            for comment in comments + line_comments:
                name = comment['user']['login']
                if name != created_by:
                    print '    comment by:', name
                    print '    body:', comment['body'].encode('utf8')
                    self.increment(name)
                    self.name_to_user[name].comments.append(comment)

    def pull_recent(self):
        for page in range(1, 3) if self.testing else range(1, 5):
            self.pull_page(page)

        for attr in 'score', 'get_total_chars', 'merges':
            def get_val(user):
                val = getattr(user, attr)
                return val() if callable(val) else val

            ordered_users = sorted(self.name_to_user.values(), key=lambda user: -get_val(user))

        users_by_score = sorted(self.name_to_user.values(), key=lambda user: -user.score)
        return users_by_score


    def increment(self, name):
        self.name_to_user.setdefault(name, User(name))
        self.name_to_user[name].score += 1

def test(testing=('test' in sys.argv[-1])):

    # repo_url = 'https://api.github.com/repos/gigwalk-corp/gigwalk_apps_platform'
    repo_url = 'https://api.github.com/repos/gigwalk-corp/gigwalk_apps_platform_api'

    puller = Puller(repo_url, testing)
    users_by_score = puller.pull_recent()

    all_results_json = json.dumps([user.to_slack_dict() for user in users_by_score], indent=2)
    print 'slack_dicts:', all_results_json

    all_results_json = json.dumps(
        [user.to_full_report_dict() for user in users_by_score], indent=2)
    print 'full_dicts:', all_results_json


if __name__ == '__main__':
    test(testing=True)
