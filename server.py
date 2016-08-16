import os, json, re
from functools import wraps

import flask
from flask import request, Response

import secrets

app = flask.Flask(__name__)
port = int(os.environ.get('PORT', 3000))


def check_auth(username, password):
    return username == secrets.server_username and password == secrets.server_password

def authenticate():
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated


@app.route('/')
def index():
    return 'hello world'

@app.route('/<repo_name>/<timestamp>')
@requires_auth
def render(repo_name, timestamp):
    if not re.match('^[a-zA-Z_\-]+$', repo_name) or not re.match('^[0-9\-_]+$', timestamp):
        return 'bad request'
    try:
        with open(os.path.join('reports', repo_name, timestamp)) as f:
            text = f.read()
    except IOError:
        return 'Report not found'
    text = 'TODO: FORMATTING<br/>' + '-' * 50 + '<br/>' + text
    return text

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 3000.
    app.run(host='0.0.0.0', port=port, debug=(port==3000))
