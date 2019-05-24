from app import db
from dtos.responses.clients import *
from dtos.responses.teams import *
from models.authentication import Authenticator
from tables.users import *
from models.constants import TeamRoles
from sqlalchemy import exc, and_

import logging


class TeamService:

    @classmethod
    def logger(cls):
        return logging.getLogger(cls.__name__)

    @classmethod
    def create_team(cls, new_team_data):
        user = Authenticator.authenticate(new_team_data)
        new_team = TeamTableEntry(
            team_name=new_team_data.team_name,
            location=new_team_data.location,
            description=new_team_data.description,
            welcome_message=new_team_data.welcome_message
        )

        try:
            db.session.add(new_team)
            db.session.flush()
            new_user_by_team = UsersByTeamsTableEntry(
                user_id=user.user_id,
                team_id=new_team.team_id,
                role=TeamRoles.CREATOR.value
            )
            db.session.add(new_user_by_team)
            db.session.flush()
            db.session.commit()
            cls.logger().info(f"Team #{new_team.team_id} created.")
            cls.logger().info(
                f"User #{user.user_id} assigned as team #{new_team.team_id} ({new_team.team_name}) {new_user_by_team.role}.")
        except exc.IntegrityError:
            db.session.rollback()
            if db.session.query(TeamTableEntry).filter(TeamTableEntry.team_name == new_team_data.team_name).first():
                cls.logger().info(
                    f"Failing to create team {new_team_data.team_name}. Name already in use for other team.")
                return TeamAlreadyCreatedResponse(f"Name {new_team_data.team_name} already in use for other team.")
            else:
                cls.logger().info(f"Failing to create team {new_team_data.team_name}.")
                return UnsuccessfulTeamResponse("Couldn't create team.")
        else:
            return SuccessfulTeamResponse(new_team)

    @classmethod
    def register_user_team(cls, registration_data):
        team_admin = Authenticator.authenticate_admin(registration_data)

        if db.session.query(UsersByTeamsTableEntry).filter(and_(
            UsersByTeamsTableEntry.user_id == registration_data.user_addable_id,
            UsersByTeamsTableEntry.team_id == registration_data.team_id
        )).one_or_none():
            return RelationAlreadyCreatedResponse("The given user already belongs to the team.")

        new_user_by_team = UsersByTeamsTableEntry(
            user_id=registration_data.user_addable_id,
            team_id=registration_data.team_id,
            role=registration_data.role
        )

        try:
            db.session.add(new_user_by_team)
            db.session.flush()
            db.session.commit()
            cls.logger().info(
                f"User #{registration_data.user_addable_id} added to team #{registration_data.team_id} as {new_user_by_team.role} by {team_admin.username}.")
        except exc.IntegrityError:
            db.session.rollback()
            if not db.session.query(UserTableEntry).filter(
                    UserTableEntry.user_id == registration_data.user_addable_id).one_or_none():
                cls.logger().info(
                    f"Failing to add user #{registration_data.team_id} to team #{registration_data.team_id}. User not found.")
                raise UserNotFoundError("User not found.", UserResponseStatus.USER_NOT_FOUND.value)
            else:
                return UnsuccessfulTeamResponse("Couldn't add user to team.")
        else:
            return SuccessfulUserAddedResponse("User added.")
