import os

from flask import Flask
from flask_pyoidc import OIDCAuthentication
from flask_pyoidc.provider_configuration import ProviderConfiguration, ClientMetadata


app = Flask(__name__)

_root_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
app.config.from_pyfile(os.path.join(_root_dir, 'config.env.py'))

DEBUG_MODE = app.config['DEBUG']

CSH_AUTH_CONFIG = ProviderConfiguration(issuer=app.config['CSH_OIDC_ISSUER'],
                                   client_metadata=ClientMetadata(app.config['CSH_OIDC_CLIENT_ID'],
                                                                  app.config['CSH_OIDC_CLIENT_SECRET']))

GOOGLE_AUTH_CONFIG = ProviderConfiguration(issuer=app.config['GGL_OIDC_ISSUER'],
                                   client_metadata=ClientMetadata(app.config['GGL_OIDC_CLIENT_ID'],
                                                                  app.config['GGL_OIDC_CLIENT_SECRET']))

auth = OIDCAuthentication({'csh': CSH_AUTH_CONFIG, 'google': GOOGLE_AUTH_CONFIG}, app)


@app.route('/')
def index():
    return '''
    <p>Hello, world! 2</p>
    <a href="/auth/google">Click here 4 google</a>
    <a href="/auth/csh">Click here 4 csh</a>
    '''

from fcwebapp.utils import needs_auth

@app.route('/home')
@needs_auth
def home():
    return "<h1>hey look it worked!</h1>"