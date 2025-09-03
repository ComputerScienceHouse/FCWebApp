import os
import uuid
from datetime import datetime

from flask import Flask, render_template, request
from flask_pyoidc import OIDCAuthentication
from flask_pyoidc.provider_configuration import ProviderConfiguration, ClientMetadata

from fcwebapp.models import UserInfo, tents, hammocks, Hammock, Tent

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
def home(user: UserInfo):
    return render_template('home.html', title='Home', user=user, year=datetime.now().year)


@app.route('/sleeping_board')
@needs_auth
def sleeping_board(user: UserInfo):
    return render_template('sleeping_board.html', title='Sleeping Board', user=user, tents=tents.values(), hammocks=hammocks.values())

@app.route('/sleeping_board', methods=['POST'])
@needs_auth
def sleeping_board_post(user: UserInfo):
    sleeptype = next(iter(request.form.keys())).split('-')[1]
    new_uuid = uuid.uuid4()
    match sleeptype:
        case 'hammock':
            while new_uuid in hammocks.keys():
                new_uuid = uuid.uuid4()
            hammocks[new_uuid] = Hammock(uuid=new_uuid, name=request.form.get('new-hammock-name'), occupant=user)
            print(hammocks[new_uuid])
        case 'tent':
            while new_uuid in tents.keys():
                new_uuid = uuid.uuid4()
            tents[new_uuid] = Tent(uuid=new_uuid, name=request.form.get('new-tent-name'), capacity=int(request.form.get('new-tent-cap')))
    return sleeping_board()