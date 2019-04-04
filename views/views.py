from models.constants import StatusCode
from models.models import Message
from models.users import RegularUser
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
    emails = [user.email() for user in all_users]
    return "Usuarios: " + ", ".join(emails)


@app.route('/users/new-user', methods=['POST'])
def register_user():
    data = request.get_json()
    new_user = RegularUser.new_with(data["username"], data["email"], data["password"])
    return jsonify(new_user), StatusCode.OK.value


@app.route('/users/login', methods=['POST'])
def login():
    data = request.get_json()
    login_user = RegularUser.login(data["email"], data["password"])

    if login_user:
        return jsonify(login_user), StatusCode.OK.value
    else:
        return jsonify({"message": "User not found"}), StatusCode.NOT_FOUND.value
