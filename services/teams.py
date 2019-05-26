from app import db
from dtos.responses.clients import *
from dtos.responses.teams import *
from models.authentication import Authenticator
from tables.users import *
from tables.teams import *
from models.constants import TeamRoles
from sqlalchemy import exc, and_

import logging


class TeamService:

    @classmethod
    def logger(cls):
        return logging.getLogger(cls.__name__)

    @classmethod
    def create_team(cls, new_team_data):
        user = Authenticator.authenticate(new_team_data.authentication)
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
    def invite_user(cls, invite_data):
        team_admin = Authenticator.authenticate_admin(invite_data.authentication)

        already_member = db.session.query(
            UserTableEntry.user_id
        ).join(
            UsersByTeamsTableEntry,
            and_(
                UserTableEntry.user_id == UsersByTeamsTableEntry.user_id,
                UserTableEntry.email == invite_data.email
            )
        ).one_or_none()

        if already_member:
            return RelationAlreadyCreatedResponse("This user already belongs to the team.")

        new_invite = TeamsInvitesTableEntry(
            team_id=invite_data.authentication.team_id,
            email=invite_data.email,
            invite_token=Authenticator.team_generate()
        )

        try:
            db.session.add(new_invite)
            db.session.flush()
            db.session.commit()
            cls.logger().info(
                f"New invitation for {new_invite.email} to join team #{new_invite.team_id}, by {team_admin.username}.")
        except exc.IntegrityError:
            db.session.rollback()
            return UnsuccessfulTeamResponse("Couldn't invite user to team.")
        else:
            return SuccessfulUserAddedResponse("User invited.")

    @classmethod
    def accept_invite(cls, invitation_data):
        user = Authenticator.authenticate(invitation_data.authentication)
        invite = db.session.query(TeamsInvitesTableEntry).filter(and_(
            TeamsInvitesTableEntry.team_id == invitation_data.team_id, TeamsInvitesTableEntry.email == user.email))\
            .one_or_none()

        if not invite or invite.invite_token != invitation_data.invite_token:
            if db.session.query(UsersByTeamsTableEntry).filter(and_(
                    UsersByTeamsTableEntry.user_id == user.user_id, UsersByTeamsTableEntry.team_id == invite.team_id))\
                    .one_or_none():
                return RelationAlreadyCreatedResponse("You are already part of this team.")
            else:
                return WrongCredentialsResponse("You weren't invited to this team.")

        new_user_team = UsersByTeamsTableEntry(
            user_id=user.user_id,
            team_id=invite.team_id,
            role=TeamRoles.MEMBER.value
        )

        try:
            db.session.add(new_user_team)
            db.session.flush()
            db.session.delete(invite)
            db.session.flush()
            db.session.commit()
            cls.logger().info(
                f"User #{user.user_id} joined team #{invite.team_id}.")
        except exc.IntegrityError:
            db.session.rollback()
            return UnsuccessfulTeamResponse("Couldn't join team.")
        else:
            return SuccessfulUserAddedResponse("Team joined!")
