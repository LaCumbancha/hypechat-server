from models.authentication import Authenticator
from models.request import ClientRequest
from services.message import MessageService

from flask import request
from run import app

import logging
logger = logging.getLogger("MessagesController")


@app.route('/messages', methods=['GET'])
def get_messages():
    logger.info("Attempting to get messages")
    req = ClientRequest(request)
    Authenticator.authenticate(req.authentication_data())
    messages = MessageService.query.all()
    contents = [message.text_content() for message in messages]
    return "Mensajes: " + ", ".join(contents)
