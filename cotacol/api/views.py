from http import HTTPStatus
from flask import Blueprint, jsonify, request, url_for

from cotacol.extensions import cache
from .services import get_climbs, get_geojson


api: Blueprint = Blueprint("api", __name__)


@api.route("/")
def index():
    return jsonify(
        {"climbs": url_for("api.climb_list", _external=True), "geojson": url_for("api.geojson", _external=True),}
    )


@api.route("/v1/climbs.geojson")
@cache.cached(timeout=3600)
def geojson():
    res = jsonify(get_geojson())
    res.mimetype = "application/geo+json"
    return res


@api.route("/v1/climbs/")
@cache.memoize(timeout=3600)
def climb_list():
    show_coordinates = False if request.args.get("without_coordinates") is not None else True
    return jsonify([climb.asdict(include_coordinates=show_coordinates) for climb in list(get_climbs().values())])


@api.route("/v1/climbs/<int:climb_id>/")
@cache.cached(timeout=3600)
def climb_detail(climb_id: int):
    try:
        climb = get_climbs()[climb_id]
    except KeyError:
        return jsonify({"message": "Climb not found."}), HTTPStatus.NOT_FOUND

    return jsonify(climb.asdict())
