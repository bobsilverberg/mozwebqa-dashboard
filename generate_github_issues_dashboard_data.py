#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import json
import sys

from github import Github


class GithubIssuesAggregator(object):

    def __init__(self, repos_file, gh_user, gs_pass):
        self.repos_file = repos_file
        self.gh_api = Github(gh_user, gs_pass)

    def process_issues(self):
        all_issues = []
        with open('%s.txt' % self.repos_file) as f:
            self.repos = [a.split('/')[-1] for a in f.read().splitlines()]
        org = self.gh_api.get_organization('Mozilla')
        for repo in self.repos:
            print 'Retrieving issues for %s...' % repo
            issues = []
            for issue in org.get_repo(repo).get_issues(state='Open'):
                issue_dict = {'assignee': issue.assignee and issue.assignee.name or '',
                              'pullRequest': issue.pull_request and issue.pull_request.html_url or ''}
                for item in ('title', 'body', 'number', 'html_url', 'comments'):
                    issue_dict[item] = getattr(issue, item)
                labels = []
                for label in issue.labels:
                    labels.append({'name': label.name, 'color': label.color})
                issue_dict['labels'] = labels
                issues.append(issue_dict)
            all_issues.append({'repo': repo, 'issues': issues})
        with open('%s_issues.json' % self.repos_file, 'w') as outfile:
            json.dump(all_issues, outfile)
        return True


if __name__ == '__main__':

    if len(sys.argv) < 3:
        raise ValueError('Must provide Repos filename and Github User and Password.')

    print 'Starting job for %s using %s' % (sys.argv[1], sys.argv[2])
    aggregator = GithubIssuesAggregator(sys.argv[1], sys.argv[2], sys.argv[3])
    print 'Job successful: %s' % aggregator.process_issues()
