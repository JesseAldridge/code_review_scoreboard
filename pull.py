#!/usr/bin/python
import json, urllib, os
from datetime import datetime
import logging
import pylab

from requests import auth
import requests

import secrets

logging.basicConfig(filename=os.path.expanduser("~/all_prs.log"), level=logging.DEBUG)
logger = logging.getLogger('all_prs')


class User:
    def __init__(self, name):
        self.name = name
        self.score = 0
        self.merges = 0
        self.comments = []

    def to_report(self):
        return '({}, score: {}, total chars: {}, merges: {})'.format(
            self.name, self.score, self.get_total_chars(), self.merges)

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

            xs = [x for x in range(len(ordered_users))]
            ys = [get_val(user) for user in ordered_users]
            pylab.bar(xs, ys)
            pylab.xticks(
                [x + .25 for x in range(len(xs))], [user.name[:5] for user in ordered_users])
            pylab.savefig('total_{}.png'.format(attr))
            pylab.cla()

        users_by_score = sorted(self.name_to_user.values(), key=lambda user: -user.score)
        results_str = [u.to_report() for u in users_by_score]
        print 'results_str:', results_str
        return results_str

    def increment(self, name):
        self.name_to_user.setdefault(name, User(name))
        self.name_to_user[name].score += 1

if __name__ == '__main__':
    testing = False

    repo_url = 'https://api.github.com/repos/gigwalk-corp/gigwalk_apps_platform'
    # repo_url = 'https://api.github.com/repos/gigwalk-corp/gigwalk_apps_platform_api'

    puller = Puller(repo_url, testing)

    results = puller.pull_recent()

    # with open('results.txt', 'a') as f:
    #     f.write('{} {}\n'.format(datetime.now(), results))
