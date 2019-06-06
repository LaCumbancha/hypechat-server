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
        register_headers(response, new_user.headers())

    return response, new_user.status_code()


@app.route('/users/login', methods=['POST'])
def login():
    logger.info("Attempting to login")
    req = ClientRequest(request)
    login_user = UserService.login_user(req.login_data())

    response = jsonify(login_user.json())
    if login_user.headers():
        register_headers(response, login_user.headers())

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


def register_headers(response, header):
    response.headers["X-Auth-Token"] = header.get("auth_token")
    response.headers['Access-Control-Expose-Headers'] = 'X-Auth-Token'


@app.route('/users/teams', methods=['GET'])
def get_user_teams():
    logger.info(f"Attempting to get teams for user.")
    req = ClientRequest(request)
    teams = UserService.teams_for_user(req.authentication_data())
    return jsonify(teams.json()), teams.status_code()


@app.route('/users/profile', methods=['PATCH'])
def update_user():
    logger.info("Attempting to update user information.")
    req = ClientRequest(request)
    updated_user = UserService.update_user(req.user_update())
    return jsonify(updated_user.json()), updated_user.status_code()


@app.route('/users/profile', methods=['GET'])
def user_profile():
    logger.info("Attempting to get user profile.")
    req = ClientRequest(request)
    user = UserService.user_profile(req.authentication_data())
    return jsonify(user.json()), user.status_code()
