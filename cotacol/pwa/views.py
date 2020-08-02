from flask import Blueprint


pwa: Blueprint = Blueprint("pwa", __name__)


@pwa.route("/")
def homepage():
    return "Coming soon!"
