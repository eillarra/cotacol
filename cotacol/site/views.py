from flask import Blueprint, render_template, send_from_directory
from os import path


site: Blueprint = Blueprint("site", __name__, template_folder="templates", static_folder="static")


@site.route("/favicon.ico")
def favicon():
    return send_from_directory(
        path.join(site.root_path, "static"), "favicon.ico", mimetype="image/vnd.microsoft.icon"
    )


@site.route("/")
def index():
    return render_template("site/index.html")
