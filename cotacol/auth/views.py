import requests

from flask import Blueprint, redirect, session, url_for

from cotacol.extensions import oauth


auth: Blueprint = Blueprint("auth", __name__)


@auth.route("/login/")
def login():
    redirect_uri = url_for(".authorize", _external=True)
    return oauth.strava.authorize_redirect(redirect_uri)


@auth.route("/authorize/strava/")
def authorize():
    token = oauth.strava.authorize_access_token()
    res = requests.get('https://api.cotacol.cc/auth/token/', {
        "provider": "strava",
        "token": token['refresh_token'],
    })
    session['jwt'] = res.text
    return redirect(url_for("site.index"))


@auth.route("/logout/")
def logout():
    session['jwt'] = "null"
    return redirect(url_for("site.index"))
