import uuid
from functools import wraps
from typing import TypeVar, Callable, Any, cast

import requests
from flask import session, redirect

from fcwebapp import app, auth, UserInfo
from fcwebapp.db import add_user, google_uuids, add_google_user
from fcwebapp.models import users

WrappedFunc = TypeVar('WrappedFunc', bound=Callable)

"""
AUTHENTICATION STUFF
"""


def needs_auth(func: WrappedFunc) -> WrappedFunc:
    """
    Decorator for ensuring authentication    """

    @wraps(func)
    def wrapped_function(*args: list, **kwargs: Any) -> Any:
        # if app.config['DEBUG']:
        #     return func(*args, **kwargs)
        match session.get('provider'):
            case 'csh':
                csh_auth()
                oidc_info = session['userinfo']
                user_uuid = uuid.UUID(oidc_info['uuid'])
                username = oidc_info['preferred_username']
            case 'google':
                if not google_auth():
                    return '''<h1>You're not authorized for this app.</h1>'''
                oidc_info = session['userinfo']
                sub = oidc_info['sub']
                if sub not in google_uuids:
                    add_google_user(sub, uuid.uuid4())
                user_uuid = google_uuids[sub]
                username = oidc_info['email'].split('@')[0]
            case _:
                return redirect(app.config['PROTOCOL'] + app.config['BASE_URL'], code=301)
        # TODO: compute data for the user
        if user_uuid not in users:
            add_user(UserInfo(user_uuid, username, oidc_info['name'], oidc_info['email']))

        kwargs['user'] = users[user_uuid]

        return func(*args, **kwargs)

    return cast(WrappedFunc, wrapped_function)


@auth.oidc_auth('csh')
def csh_auth():
    return


@auth.oidc_auth('google')
def google_auth():
    if session['userinfo']['email'].split('@')[1] != 'g.rit.edu':
        return False
    return True


@app.route('/auth/csh')
@auth.oidc_auth('csh')
def csh_login():
    session['provider'] = 'csh'
    return redirect('/home', code=301)


@app.route('/auth/google')
@auth.oidc_auth('google')
def google_login():
    session['provider'] = 'google'
    return redirect('/home', code=301)


"""
OTHER UTILS
"""

_access_token = ''


def oidc_service_account_login():
    global _access_token
    r = requests.post(app.config['CSH_OIDC_ISSUER'] + '/protocol/openid-connect/token',
                      data={'grant_type': 'client_credentials',
                            'client_id': app.config['CSH_OIDC_CLIENT_ID'],
                            'client_secret': app.config['CSH_OIDC_CLIENT_SECRET']},
                      headers={'Content-Type': 'application/x-www-form-urlencoded'})
    _access_token = r.json()['access_token']


def get_token():
    global _access_token
    r = requests.get(app.config['CSH_OIDC_ISSUER'] + '/protocol/openid-connect/userinfo',
                     headers={'Authorization': 'Bearer {}'.format(_access_token)})
    if r.status_code != 200:
        oidc_service_account_login()
    r = requests.get(app.config['CSH_OIDC_ISSUER'] + '/protocol/openid-connect/userinfo',
                     headers={'Authorization': 'Bearer {}'.format(_access_token)})
    if r.status_code != 200:
        print(r.text)
        return None
    return {'Authorization': 'Bearer {}'.format(_access_token)}


@app.context_processor
def function_map():
    return dict(len=len)
