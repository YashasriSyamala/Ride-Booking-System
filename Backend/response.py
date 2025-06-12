from flask import make_response, jsonify
from bson import json_util
class Response:
    @staticmethod
    def generate(status: str = 500, message: str = "", data=None):
        response = {
            "status": status,
            "message": message,
            "data": data
        }
        return make_response(json_util.dumps(response), status)