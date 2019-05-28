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

    response = jsonify(new_user.json())
    if new_user.headers():
        register_token_headers(response, new_user.headers())

    return response, new_user.status_code()


@app.route('/users/<searched_username>', methods=['GET'])
def search_user(searched_username):
    logger.info("Attempting to search for user")
    req = ClientRequest(request)
    found_users = UserService.search_users(req.search_users_data(searched_username))
    return jsonify(found_users.json()), found_users.status_code()


@app.route('/users/login', methods=['POST'])
def login():
    logger.info("Attempting to login")
    req = ClientRequest(request)
    login_user = UserService.login_user(req.login_data())

    response = jsonify(login_user.json())
    if login_user.headers():
        register_token_headers(response, login_user.headers())

    return response, login_user.status_code()


@app.route('/users/logout', methods=['POST'])
def logout():
    logger.info("Attempting to logout")
    req = ClientRequest(request)
    logout_user = UserService.logout_user(req.authentication_data())
    return jsonify(logout_user.json()), logout_user.status_code()


@app.route('/users/online', methods=['PUT'])
def set_online():
    logger.info("Attempting to set user online")
    req = ClientRequest(request)
    online_user = UserService.set_user_online(req.authentication_data())
    return jsonify(online_user.json()), online_user.status_code()


@app.route('/users/offline', methods=['PUT'])
def set_offline():
    logger.info("Attempting to set user offline")
    req = ClientRequest(request)
    offline_user = UserService.set_user_offline(req.authentication_data())
    return jsonify(offline_user.json()), offline_user.status_code()


def register_token_headers(response, headers):
    response.headers["X-Auth-Username"] = headers.get("username")
    response.headers["X-Auth-Token"] = headers.get("auth_token")
    response.headers['Access-Control-Expose-Headers'] = 'X-Auth-Username'
    response.headers['Access-Control-Expose-Headers'] = 'X-Auth-Token'
