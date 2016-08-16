import os

from fabric import api

env = api.env

proj_path = os.path.dirname(__file__)
proj_name = os.path.basename(proj_path)

env.user = 'ubuntu'
env.hosts = ['code-review-scoreboard']
env.use_ssh_config = True


@api.task
def deploy_server():
    api.local(
        'rsync --exclude=".git" --exclude="junk" --exclude="node_modules" '
        '--exclude="*.log" -v -r {0} {1}@{2}:~'.format(
            proj_path, env.user, env.hosts[0]))

    print '--- now do: ---'
    print 'ssh {}'.format(env.hosts[0])
