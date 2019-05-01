from exceptions.exceptions import UserCreationFailureError
from models.authentication import Authenticator
from models.constants import StatusCode
from models.request import ClientRequest
from models.users import RegularUser

from flask import request, jsonify
from run import app


@app.route('/users', methods=['GET'])
def get_users():
    req = ClientRequest(request)
    Authenticator.authenticate(req.token())
    all_users = RegularUser.query.all()
    return [user.username() for user in all_users]


@app.route('/users', methods=['POST'])
def register_user():
    req = ClientRequest(request)
    new_user = RegularUser.create_user(req.username(), req.email(), req.password())
    return jsonify(new_user), StatusCode.OK.value


@app.route('/users/login', methods=['POST'])
def login():
    req = ClientRequest(request)
    login_user = RegularUser.login_user(req.email(), req.password())
    return jsonify(login_user), StatusCode.OK.value


@app.route('/users/logout', methods=['POST'])
def logout():
    req = ClientRequest(request)
    logout_user = RegularUser.logout_user(req)
    return jsonify(logout_user), StatusCode.OK.value
