from models.request import ClientRequest
from services.messages import MessageService

from flask import request, jsonify
from run import app

import logging
logger = logging.getLogger("MessagesController")


@app.route('/messages', methods=['GET'])
def get_preview_messages():
    logger.info("Attempting to get all preview messages from user.")
    req = ClientRequest(request)
    messages = MessageService.get_preview_messages(req.authentication_data())
    return jsonify(messages.json()), messages.status_code()


@app.route('/messages/:chat_id', methods=['GET'])
def get_messages_from_chat():
    logger.info("Attempting to get all messages from specific chat from user.")
    req = ClientRequest(request)
    messages = MessageService.get_messages_from_chat(req.chat_data())
    return jsonify(messages.json()), messages.status_code()


@app.route('/messages', methods=['POST'])
def send_messages():
    logger.info("Attempting to send message.")
    req = ClientRequest(request)
    response = MessageService.send_message(req.chat_data())
    return jsonify(response.json()), response.status_code()
