import os
import uuid
from datetime import datetime

from flask import Flask, render_template, request, redirect
from flask_pyoidc import OIDCAuthentication
from flask_pyoidc.provider_configuration import ProviderConfiguration, ClientMetadata

from fcwebapp.models import UserInfo, tents, hammocks, Hammock, Tent, users

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
    auth_request_params={"scope": ["openid", "profile", "email"]},
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
from fcwebapp.db import init_db, add_hammock, update_user, join_tent, leave_tent, add_tent, rm_hammock


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
    """
    sleeptype - hammock or tent
    action - add, join, leave
    occupying - id or name
    """
    data = request.form
    sleeptype = data['sleeptype']
    occupying = data['occupying']
    capacity = data.get('capacity')
    match data['action']:
        case "add":
            new_uuid = uuid.uuid4()
            while new_uuid in hammocks.keys() or new_uuid in tents.keys():
                new_uuid = uuid.uuid4()
            if sleeptype == "hammock":
                add_hammock(Hammock(new_uuid, name=occupying, occupant=user))
                user.occupying_uuid = new_uuid
                update_user(user)
            elif sleeptype == "tent":
                add_tent(Tent(new_uuid, name=occupying, capacity=capacity))
        case "join":
            occupying = uuid.UUID(occupying)
            if sleeptype != "tent" or occupying not in tents.keys():
                return redirect("/sleeping_board", code=400)
            join_tent(tents[occupying], user)
            return redirect("/sleeping_board", code=302)
        case "leave":
            occupying = uuid.UUID(occupying)
            if sleeptype == "hammock":
                if occupying not in hammocks.keys():
                    return redirect("/sleeping_board", code=400)
                rm_hammock(hammocks[occupying])
            elif sleeptype == "tent":
                if occupying not in tents.keys():
                    return redirect("/sleeping_board", code=400)
                leave_tent(tents[occupying], user)
            else:
                return redirect("/sleeping_board", code=400)
            user.occupying_uuid = None
            update_user(user)
        case _:
            print('SOMEONE FUCKED UP AND IT\'S NOT A TENT OR HAMMOCK')
            return redirect('/sleeping_board', code=302)
    return redirect('/sleeping_board', code=302)


@app.route('/profile')
@needs_auth
def profiles(user: UserInfo):
    return render_template('profiles.html', title='Profile', user=user)


@app.route('/admin')
@needs_auth
def admin(user: UserInfo):
    # if user.username == 'andyp' or user.username == 'mob':
    return render_template('admin.html', title='Admin Panel', user=user,
                           users=sorted(users.values(), key=lambda u: u.name), event_id=561)
    return redirect('/home', code=302)


@app.route('/profile/edit', methods=['POST'])
@needs_auth
def profile_edit(user: UserInfo):
    for k, v in request.form.items():
        print(k, v)
        match k:
            case 'phone_number':
                num = v.strip().replace(' ', '').replace('-', '').replace('_', '')
                user.phone_number = num
            case 'allergy':
                user.allergy = v
            case 'diet':
                user.diet = v
            case 'health':
                user.health = v
            case 'in_ride_toggle':
                user.in_ride = not user.in_ride
            case _:
                return redirect('/profile', code=302)
        update_user(user)
    return redirect('/profile', code=302)


init_db()
