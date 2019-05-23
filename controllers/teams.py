from models.constants import StatusCode
from models.request import ClientRequest
from services.teams import TeamService

from flask import request, jsonify
from run import app

import logging
logger = logging.getLogger("TeamsController")


@app.route('/teams', methods=['POST'])
def register_team():
    logger.info("Attempting to register new team")
    req = ClientRequest(request)
    new_team = TeamService.create_team(req.new_team_data())
    return jsonify(new_team.json()), new_team.status_code()
