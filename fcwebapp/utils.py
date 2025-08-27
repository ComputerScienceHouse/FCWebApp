from functools import wraps
from typing import TypeVar, Callable, Any, cast

from flask import session, redirect

from fcwebapp import app, auth

WrappedFunc = TypeVar('WrappedFunc', bound=Callable)


def needs_auth(func: WrappedFunc) -> WrappedFunc:
    """
    Decorator for ensuring authentication    """

    @wraps(func)
    def wrapped_function(*args: list, **kwargs: dict) -> Any:
        print('hello world')
        match session.get('provider'):
            case 'csh':
                print('hi1')
                csh_auth()
            case 'google':
                print('hi2')
                google_auth()
            case _:
                print('hi')
                return redirect(app.config['PROTOCOL'] + app.config['BASE_URL'], code=301)
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