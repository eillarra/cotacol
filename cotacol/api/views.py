from http import HTTPStatus
from flask import Blueprint, jsonify, request, send_from_directory, url_for
from flask_login import current_user, login_required  # type: ignore
from os import path

from cotacol.extensions import cache, db
from cotacol.models import Climb, User


api: Blueprint = Blueprint("api", __name__)


@api.route("/")
def index():
    return jsonify(
        {
            "climbs": url_for("api.climb_list", _external=True),
            "geojson": url_for("api.geojson", _external=True),
        }
    )


@api.route("/v1/climbs.geojson")
@cache.cached(timeout=3600)
def geojson():
    return send_from_directory(
        path.join(api.root_path, "..", "data"), "cotacol.geojson", mimetype="application/geo+json"
    )


@api.route("/v1/climbs/")
@cache.memoize(timeout=3600)
def climb_list():
    return jsonify([climb.as_dict(exclude_coordinates=True) for climb in Climb.query.all()])


@api.route("/v1/climbs/<int:climb_id>/")
@cache.cached(timeout=3600)
def climb_detail(climb_id: int):
    climb = Climb.query.get(climb_id)

    if not climb:
        return jsonify({"message": "Climb not found."}), HTTPStatus.NOT_FOUND

    return jsonify(climb.as_dict())


@api.route("/v1/user/", methods=["get"])
@login_required
def user_detail():
    return jsonify(current_user.as_dict())


@api.route("/v1/user/", methods=["put"])
@login_required
def user_update():
    user = User.query.get(current_user.id)
    user.extra_data = request.json["extra_data"]
    db.session.commit()
    return jsonify(user.as_dict())
