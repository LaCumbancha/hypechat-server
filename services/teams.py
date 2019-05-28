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
                return BadRequestTeamResponse(f"Name {new_team_data.team_name} already in use for other team.",
                                              TeamResponseStatus.ALREADY_REGISTERED.value)
            else:
                cls.logger().info(f"Failing to create team {new_team_data.team_name}.")
                return UnsuccessfulTeamResponse("Couldn't create team.")
        else:
            return SuccessfulTeamCreatedResponse(new_team)

    @classmethod
    def invite_user(cls, invite_data):
        team_admin = Authenticator.authenticate_team(invite_data.authentication, lambda user: TeamRoles.is_admin(user))

        already_member = db.session.query(
            UserTableEntry.user_id
        ).join(
            UsersByTeamsTableEntry,
            and_(
                UsersByTeamsTableEntry.team_id == invite_data.authentication.team_id,
                UserTableEntry.user_id == UsersByTeamsTableEntry.user_id,
                UserTableEntry.email == invite_data.email
            )
        ).one_or_none()

        if already_member:
            return BadRequestTeamResponse("This user already belongs to the team.",
                                          TeamResponseStatus.ALREADY_REGISTERED.value)

        if db.session.query(TeamsInvitesTableEntry).filter(and_(
                TeamsInvitesTableEntry.team_id == invite_data.authentication.team_id,
                TeamsInvitesTableEntry.email == invite_data.email
        )).one_or_none():
            return BadRequestTeamResponse("This user was already invited to join the team.",
                                          TeamResponseStatus.ALREADY_INVITED.value)

        new_invite = TeamsInvitesTableEntry(
            team_id=invite_data.authentication.team_id,
            email=invite_data.email,
            invite_token=Authenticator.team_invitation()
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
            return SuccessfulTeamResponse("User invited.", TeamResponseStatus.USER_INVITED.value)

    @classmethod
    def accept_invite(cls, invitation_data):
        user = Authenticator.authenticate(invitation_data.authentication)
        invite = db.session.query(TeamsInvitesTableEntry).filter(and_(
            TeamsInvitesTableEntry.team_id == invitation_data.team_id, TeamsInvitesTableEntry.email == user.email)) \
            .one_or_none()

        if not invite or invite.invite_token != invitation_data.invite_token:
            if db.session.query(UsersByTeamsTableEntry).filter(and_(
                    UsersByTeamsTableEntry.user_id == user.user_id,
                    UsersByTeamsTableEntry.team_id == invitation_data.team_id)
            ).one_or_none():
                return BadRequestTeamResponse("You are already part of this team.",
                                              TeamResponseStatus.ALREADY_REGISTERED.value)
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
            return SuccessfulTeamResponse("Team joined!", TeamResponseStatus.USER_ADDED.value)

    @classmethod
    def team_users(cls, user_data):
        user = Authenticator.authenticate_team(user_data)

        team_users = db.session.query(
            UserTableEntry.user_id,
            UserTableEntry.username,
            UserTableEntry.first_name,
            UserTableEntry.last_name,
            UserTableEntry.profile_pic,
            UserTableEntry.online,
            UsersByTeamsTableEntry.role
        ).join(
            UsersByTeamsTableEntry,
            and_(
                UserTableEntry.user_id == UsersByTeamsTableEntry.user_id,
                UsersByTeamsTableEntry.team_id == user_data.team_id
            )
        ).all()

        cls.logger().info(f"User {user.username} got {len(team_users)} users from team #{user_data.team_id}.")
        return SuccessfulUsersListResponse(cls._team_users_list(team_users))

    @classmethod
    def _team_users_list(cls, user_list):
        users = []

        for user in user_list:
            users += [{
                "id": user.user_id,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "profile_pic": user.profile_pic,
                "online": user.online,
                "role": user.role
            }]

        return users

    @classmethod
    def delete_users(cls, delete_data):
        user = Authenticator.authenticate_team(delete_data.authentication, lambda user: TeamRoles.is_admin(user))

        delete_user = db.session.query(UsersByTeamsTableEntry).filter(and_(
            UsersByTeamsTableEntry.user_id == delete_data.delete_id,
            UsersByTeamsTableEntry.team_id == delete_data.authentication.team_id
        )).one_or_none()

        if delete_user:

            if TeamRoles.is_higher_role(user, delete_user):
                try:
                    db.session.delete(delete_user)
                    db.session.commit()
                    cls.logger().info(
                        f"User #{delete_user.user_id} deleted from team #{delete_user.team_id} by {user.username}.")
                    return SuccessfulTeamResponse("User removed!", TeamResponseStatus.USER_REMOVED.value)
                except exc.IntegrityError:
                    db.session.rollback()
                return UnsuccessfulTeamResponse("Couldn't delete user.")
            else:
                cls.logger().info(
                    f"Cannot delete user #{delete_user.user_id} because he's role ({delete_user.role})" +
                    f" is higher than yours.")
                return ForbiddenTeamResponse("You don't have enough permissions to delete this user.",
                                             TeamResponseStatus.NOT_ENOUGH_PERMISSIONS.value)

        else:
            cls.logger().info(
                f"Trying to delete user #{delete_data.delete_id}, who's not part of the team" +
                f" {delete_data.authentication.team_id}.")
            return NotFoundTeamResponse("Couldn't find user to delete", UserResponseStatus.USER_NOT_FOUND.value)

    @classmethod
    def change_role(cls, change_role_data):
        team_admin = Authenticator.authenticate_team(change_role_data.authentication,
                                                     lambda user: TeamRoles.is_creator(user))

        if change_role_data.new_role == TeamRoles.CREATOR.value:
            cls.logger().info(
                f"Trying to set user as team #{change_role_data.authentication.team_id} {TeamRoles.CREATOR.value}")
            return BadRequestTeamResponse("You cannot set someone as team CREATOR.",
                                          TeamResponseStatus.ROLE_UNAVAILABLE.value)

        user_team = db.session.query(UsersByTeamsTableEntry).filter(and_(
            UsersByTeamsTableEntry.user_id == change_role_data.user_id,
            UsersByTeamsTableEntry.team_id == change_role_data.authentication.team_id)
        ).one_or_none()

        if not user_team:
            cls.logger().info(
                f"Trying to modify role from user #{user_team.user_id}, who's not part of team #{user_team.team_id}")
            return BadRequestTeamResponse("The given user is not part this team.",
                                          TeamResponseStatus.USER_NOT_MEMBER.value)

        user_team.role = change_role_data.new_role

        try:
            db.session.add(user_team)
            db.session.commit()
            cls.logger().info(
                f"User #{user_team.user_id} setted as team #{user_team.team_id} {user_team.role} " +
                f"by {team_admin.username}.")
        except exc.IntegrityError:
            db.session.rollback()
            cls.logger().info(f"Failing to modifying role of #{user.user_id} in team #{user.team_id}.")
            return UnsuccessfulTeamResponse("Couldn't modify user role.")
        else:
            return SuccessfulTeamResponse("Role modified", TeamResponseStatus.ROLE_MODIFIED.value)

    @classmethod
    def leave_team(cls, user_data):
        user = Authenticator.authenticate_team(user_data)

        delete_user = db.session.query(UsersByTeamsTableEntry).filter(and_(
            UsersByTeamsTableEntry.user_id == user.user_id,
            UsersByTeamsTableEntry.team_id == user.team_id
        )).one_or_none()

        try:
            db.session.delete(delete_user)
            db.session.commit()
            cls.logger().info(
                f"User #{user.user_id} leaved team #{user.team_id}.")
            return SuccessfulTeamResponse("Team leaved!", TeamResponseStatus.USER_REMOVED.value)
        except exc.IntegrityError:
            db.session.rollback()
            cls.logger().info(f"User #{user.user_id} failing to leave team #{user.team_id}.")
            return UnsuccessfulTeamResponse("Couldn't leave team.")
