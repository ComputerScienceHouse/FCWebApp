from os import environ
from secrets import token_urlsafe

DEBUG = environ.get('DEBUG', False)
BASE_URL = environ.get('BASE_URL', 'http://localhost:5000')
PROTOCOL = '' if '://' in BASE_URL else environ.get('PROTOCOL', 'http')
SECRET_KEY = environ.get('SECRET_KEY', token_urlsafe(32))

OIDC_REDIRECT_URI = BASE_URL + '/auth/redirect_uri'


CSH_OIDC_ISSUER = environ.get("CSH_OIDC_ISSUER", "https://sso.csh.rit.edu/auth/realms/csh")
CSH_OIDC_CLIENT_ID = environ.get("CSH_OIDC_CLIENT_ID", "")
CSH_OIDC_CLIENT_SECRET = environ.get("CSH_OIDC_CLIENT_SECRET", "")

GGL_OIDC_ISSUER = environ.get("GGL_OIDC_ISSUER", "https://sso.csh.rit.edu/auth/realms/csh")
GGL_OIDC_CLIENT_ID = environ.get("GGL_OIDC_CLIENT_ID", "a")
GGL_OIDC_CLIENT_SECRET = environ.get("GGL_OIDC_CLIENT_SECRET", "b")