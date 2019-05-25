from models.request import ClientRequest
from services.messages import MessageService

from flask import request, jsonify
from run import app

import logging
logger = logging.getLogger("MessagesController")


@app.route('/messages/<chat_id>', methods=['GET'])
def get_messages_from_direct_chat(chat_id):
    logger.info("Attempting to get all messages from specific chat from user.")
    req = ClientRequest(request)
    messages = MessageService.get_messages_from_direct_chat(req.chat_data(chat_id))
    return jsonify(messages.json()), messages.status_code()


@app.route('/messages', methods=['POST'])
def send_direct_message():
    logger.info("Attempting to send message.")
    req = ClientRequest(request)
    response = MessageService.send_direct_message(req.inbox_data())
    return jsonify(response.json()), response.status_code()
