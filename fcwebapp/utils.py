from functools import wraps
from typing import TypeVar, Callable, Any, cast

from flask import session, redirect

from fcwebapp import app, auth, UserInfo
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
        if app.config['DEBUG']:
            return func(*args, **kwargs)
        match session.get('provider'):
            case 'csh':
                csh_auth()
            case 'google':
                google_auth()
            case _:
                return redirect(app.config['PROTOCOL'] + app.config['BASE_URL'], code=301)
        oidc_info = session['userinfo']
        # TODO: compute data for the user

        if oidc_info['uuid'] in users.keys():
            kwargs['user']=users[oidc_info['uuid']]
        else:
            newuser=UserInfo(oidc_info['uuid'], oidc_info['preferred_username'], oidc_info['name'], oidc_info['email'])
            kwargs['user']=newuser
            users[newuser.uuid]=newuser
        return func(*args, **kwargs)

    return cast(WrappedFunc, wrapped_function)

@auth.oidc_auth('csh')
def csh_auth():
    return

@auth.oidc_auth('google')
def google_auth():
    return

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

@app.context_processor
def function_map():
    return dict(len=len)