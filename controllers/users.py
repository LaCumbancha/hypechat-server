from models.authentication import Authenticator
from models.constants import StatusCode
from models.request import ClientRequest
from services.users import UserService

from flask import request, jsonify
from run import app

import logging
logger = logging.getLogger("UsersController")


@app.route('/users', methods=['GET'])
def get_users():
    logger.info("Attempting to get users")
    req = ClientRequest(request)
    Authenticator.authenticate(req.authentication_data())
    all_users = UserService.query.all()
    return [user.username() for user in all_users]


@app.route('/users', methods=['POST'])
def register_user():
    logger.info("Attempting to register new user")
    req = ClientRequest(request)
    new_user = UserService.create_user(req.new_user_data())
    return jsonify(new_user.json()), StatusCode.OK.value


@app.route('/users/login', methods=['POST'])
def login():
    logger.info("Attempting to login")
    req = ClientRequest(request)
    login_user = UserService.login_user(req.login_data())
    return jsonify(login_user), StatusCode.OK.value


@app.route('/users/logout', methods=['POST'])
def logout():
    logger.info("Attempting to logout")
    req = ClientRequest(request)
    user = Authenticator.authenticate(req.authentication_data())
    logout_user = UserService.logout_user(user)
    return jsonify(logout_user), StatusCode.OK.value
