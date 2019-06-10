from exceptions.exceptions import *
from run import app
from flask import jsonify


@app.errorhandler(HypechatError)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response
