from exceptions.exceptions import UserCreationFailureError
from models.constants import StatusCode
from models.users import RegularUser
from models.models import Message
from run import app
from flask import request, jsonify


@app.route('/messages', methods=['GET'])
def get_messages():
    all_messages = Message.query.all()
    contents = [message.text_content() for message in all_messages]
    return "Mensajes: " + ", ".join(contents)


@app.route('/users', methods=['GET'])
def get_users():
    all_users = RegularUser.query.all()
    usernames = [user.username() for user in all_users]
    return "Usuarios: " + ", ".join(usernames)


@app.route('/users/new-user', methods=['POST'])
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
    login_user = RegularUser.logout_user(data["auth_token"])

    if login_user:
        return jsonify(login_user), StatusCode.OK.value
    else:
        return jsonify({"message": "User not found"}), StatusCode.NOT_FOUND.value
