from models.authentication import Authenticator
from models.constants import StatusCode
from models.request import ClientRequest
from services.users import UserService

from flask import request, jsonify
from run import app

import logging
logger = logging.getLogger("UsersController")


@app.route('/users', methods=['POST'])
def register_user():
    logger.info("Attempting to register new user")
    req = ClientRequest(request)
    new_user = UserService.create_user(req.new_user_data())
    return jsonify(new_user.json()), new_user.status_code()


@app.route('/users/login', methods=['POST'])
def login():
    logger.info("Attempting to login")
    req = ClientRequest(request)
    login_user = UserService.login_user(req.login_data())
    return jsonify(login_user.json()), login_user.status_code()


@app.route('/users/logout', methods=['POST'])
def logout():
    logger.info("Attempting to logout")
    req = ClientRequest(request)
    logout_user = UserService.logout_user(req.authentication_data())
    return jsonify(logout_user.json()), logout_user.status_code()


@app.route('/users/online', methods=['POST'])
def set_online():
    logger.info("Attempting to set user online")
    req = ClientRequest(request)
    online_user = UserService.set_user_online(req.authentication_data())
    return jsonify(online_user.json()), online_user.status_code()


@app.route('/users/offline', methods=['POST'])
def set_offline():
    logger.info("Attempting to set user offline")
    req = ClientRequest(request)
    offline_user = UserService.set_user_offline(req.authentication_data())
    return jsonify(offline_user.json()), offline_user.status_code()
