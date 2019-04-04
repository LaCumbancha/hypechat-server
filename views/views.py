from models.constants import StatusCode
from models.users import RegularUser
from run import app
from flask import request, jsonify


@app.route('/users/new-user', methods=['POST'])
def register_user():
    data = request.get_json()
    new_user = RegularUser.create_user(data["username"], data["email"], data["password"])
    return jsonify(new_user), StatusCode.OK.value


@app.route('/users/login', methods=['POST'])
def login():
    data = request.get_json()
    login_user = RegularUser.login_user(data["email"], data["password"])

    if login_user:
        return jsonify(login_user), StatusCode.OK.value
    else:
        return jsonify({"message": "User not found"}), StatusCode.NOT_FOUND.value


@app.route('/users/logout', methods=['POST'])
def logout():
    data = request.get_json()
    login_user = RegularUser.logout_user(data["id"])

    if login_user:
        return jsonify(login_user), StatusCode.OK.value
    else:
        return jsonify({"message": "User not found"}), StatusCode.NOT_FOUND.value
