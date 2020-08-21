from flask import Blueprint, redirect, url_for
from flask_login import login_user, logout_user  # type: ignore

from cotacol.extensions import login_manager, oauth
from cotacol.models import User, user_from_token


auth: Blueprint = Blueprint("auth", __name__)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@auth.route("/login/")
def login():
    redirect_uri = url_for(".authorize", _external=True)
    return oauth.strava.authorize_redirect(redirect_uri)


@auth.route("/authorize/strava/")
def authorize():
    token = oauth.strava.authorize_access_token()
    user = user_from_token(token)
    login_user(user, remember=True)
    return redirect(url_for("site.index"))


@auth.route("/logout/")
def logout():
    logout_user()
    return redirect(url_for("site.index"))
