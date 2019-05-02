from models.authentication import Authenticator
from models.request import ClientRequest
from models.constants import StatusCode
from models.message import Message

from flask import request, jsonify
from run import app


@app.route('/messages', methods=['GET'])
def get_messages():
    req = ClientRequest(request)
    Authenticator.authenticate(req.authentication_data())
    messages = Message.query.all()
    contents = [message.text_content() for message in messages]
    return "Mensajes: " + ", ".join(contents)
