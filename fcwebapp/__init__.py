from flask import Flask
from flask_pyoidc import OIDCAuthentication
from flask_pyoidc.provider_configuration import ProviderConfiguration, ClientMetadata

app = Flask(__name__)

CSH_AUTH_CONFIG = ProviderConfiguration(issuer=app.config['CSH_OIDC_ISSUER'],
                                   client_metadata=ClientMetadata(app.config['CSH_OIDC_CLIENT_ID'],
                                                                  app.config['CSH_OIDC_CLIENT_SECRET']))

GOOGLE_AUTH_CONFIG = ProviderConfiguration(issuer=app.config['GGL_OIDC_ISSUER'],
                                   client_metadata=ClientMetadata(app.config['GGL_OIDC_CLIENT_ID'],
                                                                  app.config['GGL_OIDC_CLIENT_SECRET']))

auth = OIDCAuthentication({'csh': CSH_AUTH_CONFIG, 'google': GOOGLE_AUTH_CONFIG}, app)


@app.route('/')
def index():
    return "<p>Hello, world! 2</p>"
