import os
import uuid
from datetime import datetime

from flask import Flask, render_template, request
from flask_pyoidc import OIDCAuthentication
from flask_pyoidc.provider_configuration import ProviderConfiguration, ClientMetadata

from fcwebapp.models import UserInfo, tents, hammocks, Hammock, Tent

app = Flask(__name__)

_root_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
app.config.from_pyfile(os.path.join(_root_dir, "config.env.py"))

DEBUG_MODE = app.config["DEBUG"]

CSH_AUTH_CONFIG = ProviderConfiguration(
    issuer=app.config["CSH_OIDC_ISSUER"],
    client_metadata=ClientMetadata(
        app.config["CSH_OIDC_CLIENT_ID"], app.config["CSH_OIDC_CLIENT_SECRET"]
    ),
)

GOOGLE_AUTH_CONFIG = ProviderConfiguration(
    issuer=app.config["GGL_OIDC_ISSUER"],
    client_metadata=ClientMetadata(
        app.config["GGL_OIDC_CLIENT_ID"], app.config["GGL_OIDC_CLIENT_SECRET"]
    ),
)

auth = OIDCAuthentication({"csh": CSH_AUTH_CONFIG, "google": GOOGLE_AUTH_CONFIG}, app)


@app.route("/")
def index():
    return """
    <p>Hello, world! 2</p>
    <a href="/auth/google">Click here 4 google</a>
    <a href="/auth/csh">Click here 4 csh</a>
    """


from fcwebapp.utils import needs_auth
from fcwebapp.db import init_db, add_hammock


@app.route("/home")
@needs_auth
def home(user: UserInfo):
    return render_template(
        "home.html", title="Home", user=user, year=datetime.now().year
    )


@app.route("/sleeping_board")
@needs_auth
def sleeping_board(user: UserInfo):
    print(user)
    return render_template(
        "sleeping_board.html",
        title="Sleeping Board",
        user=user,
        tents=tents.values(),
        hammocks=hammocks.values(),
    )


@app.route("/sleeping_board", methods=["POST"])
@needs_auth
def sleeping_board_post(user: UserInfo):
    read_value = next(iter(request.form.keys())).split('-')
    sleeptype = read_value[1]
    if read_value[0] == 'join':
        tent_id=uuid.UUID(request.form.get('join-tent-id'))
        tents[tent_id].add_occupant(user)
        user.occupying_uuid = tent_id
        return sleeping_board()
    if read_value[0] == 'leave':
        tent_id=uuid.UUID(request.form.get('leave-tent-id'))
        tents[tent_id].remove_occupant(user)
        user.occupying_uuid = None
        return sleeping_board()
    new_uuid = uuid.uuid4()
    match sleeptype:
        case "hammock":
            while new_uuid in hammocks.keys():
                new_uuid = uuid.uuid4()
            add_hammock(Hammock(uuid=new_uuid, name=request.form.get('new-hammock-name'), occupant=user))
            user.occupying_uuid = new_uuid
        case "tent":
            while new_uuid in tents.keys():
                new_uuid = uuid.uuid4()
            tents[new_uuid] = Tent(
                uuid=new_uuid,
                name=request.form.get("new-tent-name"),
                capacity=int(request.form.get("new-tent-cap")),
            )
        case _:
            print("SOMEONE FUCKED UP AND IT'S NOT A TENT OR HAMMOCK")
            return sleeping_board()
    return sleeping_board()


@app.route("/profile")
@needs_auth
def profiles(user: UserInfo):
    return render_template("profiles.html", title="Profile", user=user)

init_db()
