import json

from flask import Blueprint, redirect, request, render_template, send_from_directory, session, url_for
from os import path


site: Blueprint = Blueprint("site", __name__, template_folder="templates", static_folder="static")


@site.route("/favicon.ico")
def favicon():
    return send_from_directory(path.join(site.root_path, "static"), "favicon.ico", mimetype="image/vnd.microsoft.icon")


@site.route("/")
def index():
    return render_template("site/index.html")


@site.route("/login/")
def login():
    session['jwt'] = json.dumps(request.args)
    return redirect(url_for("site.index"))


@site.route("/logout/")
def logout():
    session['jwt'] = "null"
    return redirect(url_for("site.index"))
