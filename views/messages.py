from models.authentication import Authenticator
from models.constants import StatusCode
from models.models import Message

from flask import request, jsonify
from run import app


@app.route('/messages', methods=['GET'])
def get_messages():
    req = ClientRequest(request)
    Authenticator.authenticate(req.token())
    messages = Message.query.all()
    contents = [message.text_content() for message in messages]
    return "Mensajes: " + ", ".join(contents)
