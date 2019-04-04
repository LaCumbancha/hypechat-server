from exceptions.exceptions import UserCreationFailureError
from run import app
from flask import jsonify


@app.errorhandler(UserCreationFailureError)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response
