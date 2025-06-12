from flask import Blueprint, request, current_app
import requests
from flask_jwt_extended import jwt_required
from app.utils.response import Response

coordinates_bp = Blueprint("coordinates", __name__, url_prefix="/api/coordinates")


@coordinates_bp.route("/get_places", methods=["POST"])
@jwt_required()
def get_places():
    try:
        data = request.get_json()
        search_text = data["search_text"]
        latitude = data["lat"]
        longitude = data["lng"]
        radius = 50*1000  # in meters
        GOOGLE_API_KEY = current_app.config["GOOGLE_API_KEY"]
        headers = {
            "X-Goog-Api-Key": GOOGLE_API_KEY,
            "X-Goog-FieldMask": "suggestions.placePrediction.place,suggestions.placePrediction.text",
        }

        url = "https://places.googleapis.com/v1/places:autocomplete"
        payload = {
            "input": search_text,
            "locationBias": {
                "circle": {
                    "center": {
                        "latitude": latitude,
                        "longitude": longitude,
                    },
                    "radius": radius,
                }
            },
        }
        response = requests.post(url, headers=headers, json=payload, verify=False)
        sugestions = response.json().get("suggestions", [])
        list_of_places = {}
        for place in sugestions:
            place_id = place["placePrediction"]["place"].split("/")[1]
            place_name = place["placePrediction"]["text"]["text"]
            list_of_places[place_name] = place_id
        return Response.generate(status=200, data=list_of_places)
    except Exception as e:
        return Response.generate(message=str(e))

def get_lag_and_lat(place_id):
    GOOGLE_API_KEY = current_app.config["GOOGLE_API_KEY"]
    headers = {
        "X-Goog-Api-Key": GOOGLE_API_KEY,
        "X-Goog-FieldMask": "location"
    }

    url = f"https://places.googleapis.com/v1/places/{place_id}"
    response = requests.get(url, headers=headers, verify=False)
    response = response.json()
    location = response.get("location", [])
    return [location["longitude"], location["latitude"]]
