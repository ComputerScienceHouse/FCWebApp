from functools import wraps
from typing import TypeVar, Callable, Any, cast

from flask import session, redirect

from fcwebapp import app

WrappedFunc = TypeVar('WrappedFunc', bound=Callable)


def needs_auth(func: WrappedFunc) -> WrappedFunc:
    """
    Decorator for ensuring authentication
    """

    @auth.oidc_auth('app')
    @wraps(func)
    def wrapped_function(*args: list, **kwargs: dict) -> Any:
        # Determine if user is authenticated via Google or CSH here
        username = str(session['userinfo'].get('preferred_username', ''))
        return func(*args, **kwargs)

    return cast(WrappedFunc, wrapped_function)
