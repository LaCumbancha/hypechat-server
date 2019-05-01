from exceptions.exceptions import UserCreationFailureError
from models.authentication import Authenticator
from models.constants import StatusCode
from models.users import RegularUser

from flask import request, jsonify
from run import app


@app.route('/users', methods=['GET'])
def get_users():
    data = request.get_json()
    Authenticator.authenticate(data["auth_token"])
    all_users = RegularUser.query.all()
    usernames = [user.username() for user in all_users]
    return "Usuarios: " + ", ".join(usernames)


@app.route('/users', methods=['POST'])
def register_user():
    data = request.get_json()
    new_user = RegularUser.create_user(data["username"], data["email"], data["password"])
    return jsonify(new_user), StatusCode.OK.value


@app.route('/users/login', methods=['POST'])
def login():
    data = request.get_json()
    login_user = RegularUser.login_user(data["email"], data["password"])

    return jsonify(login_user), StatusCode.OK.value


@app.route('/users/logout', methods=['POST'])
def logout():
    data = request.get_json()
    Authenticator.authenticate(data["auth_token"])
    login_user = RegularUser.logout_user(data["auth_token"])

    return jsonify(login_user), StatusCode.OK.value
