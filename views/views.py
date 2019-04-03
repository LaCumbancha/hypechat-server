from models.models import Message
from models.users import RegularUser
from run import app
from flask import request


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
def new_user():
    RegularUser.new_with(request.get_json().get("username"), request.get_json().get("email"), request.get_json().get("password"))
    return "Usuario creado"
