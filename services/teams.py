from app import db
from exceptions.exceptions import *
from dtos.responses.clients import *
from dtos.responses.teams import *
from dtos.responses.channels import SuccessfulChannelsListResponse
from dtos.model import TeamInvitationEmailDTO
from models.authentication import Authenticator
from services.emails import EmailService
from tables.users import *
from tables.teams import *
from tables.channels import *
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
            picture=new_team_data.picture,
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
                return BadRequestTeamMessageResponse(f"Name {new_team_data.team_name} already in use for other team.",
                                                     TeamResponseStatus.ALREADY_REGISTERED.value)
            else:
                cls.logger().error(f"Failing to create team {new_team_data.team_name}.")
                return UnsuccessfulTeamMessageResponse("Couldn't create team.")
        else:
            return SuccessfulTeamResponse(new_team, TeamResponseStatus.CREATED.value)

    @classmethod
    def add_user(cls, add_data):
        admin = Authenticator.authenticate(add_data.authentication)

        if admin.role == UserRoles.ADMIN.value:
            user = db.session.query(UserTableEntry).filter(UserTableEntry.user_id == add_data.add_user_id).one_or_none()

            if not user:
                cls.logger().info(f"User {add_data.add_user_id} not found.")
                raise UserNotFoundError("User not found.", UserResponseStatus.USER_NOT_FOUND.value)

            if db.session.query(UsersByTeamsTableEntry).filter(and_(
                UsersByTeamsTableEntry.user_id == user.user_id,
                UsersByTeamsTableEntry.team_id == add_data.authentication.team_id
            )).one_or_none():
                cls.logger().info(f"User {add_data.add_user_id} already part of team #{add_data.authentication.team_id}.")
                return BadRequestTeamMessageResponse("This user already belongs to the team.",
                                                     TeamResponseStatus.ALREADY_REGISTERED.value)

            previous_invitation = db.session.query(TeamsInvitesTableEntry).filter(
                TeamsInvitesTableEntry.team_id == add_data.authentication.team_id,
                TeamsInvitesTableEntry.email == admin.username
            ).one_or_none()

            if previous_invitation:
                cls.logger().info(f"Deleting old invitation for user {add_data.add_user_id} to team "
                                  f"#{add_data.authentication.team_id}.")
                db.session.delete(previous_invitation)
                db.session.commit()

            added_user = UsersByTeamsTableEntry(user_id=add_data.add_user_id, team_id=add_data.authentication.team_id)

            try:
                db.session.add(added_user)
                db.session.commit()
                cls.logger().info(
                    f"Added user #{added_user.user_id} to team #{added_user.team_id} by admin {admin.username}.")
                return SuccessfulTeamMessageResponse("User added.", TeamResponseStatus.ADDED.value)

            except exc.IntegrityError:
                db.session.rollback()
                cls.logger().error(
                    f"Couldn't add user #{added_user.user_id} to team #{added_user.team_id}.")
                return UnsuccessfulTeamMessageResponse("Couldn't invite user to team.")

        else:
            raise NoPermissionsError("You must be ADMIN to perform this action.",
                                     TeamResponseStatus.NOT_ENOUGH_PERMISSIONS.value)

    @classmethod
    def invite_user(cls, invite_data):
        team_admin = Authenticator.authenticate_team(invite_data.authentication, TeamRoles.is_team_admin)

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
            return BadRequestTeamMessageResponse("This user already belongs to the team.",
                                                 TeamResponseStatus.ALREADY_REGISTERED.value)

        if db.session.query(TeamsInvitesTableEntry).filter(and_(
                TeamsInvitesTableEntry.team_id == invite_data.authentication.team_id,
                TeamsInvitesTableEntry.email == invite_data.email
        )).one_or_none():
            return BadRequestTeamMessageResponse("This user was already invited to join the team.",
                                                 TeamResponseStatus.ALREADY_INVITED.value)

        invite_token = Authenticator.team_invitation()
        new_invite = TeamsInvitesTableEntry(
            team_id=invite_data.authentication.team_id,
            email=invite_data.email,
            invite_token=invite_token
        )

        try:
            db.session.add(new_invite)
            db.session.flush()
            db.session.commit()
            cls.logger().info(
                f"New invitation for {new_invite.email} to join team #{new_invite.team_id}, by {team_admin.username}.")

            email_data = TeamInvitationEmailDTO(
                email=invite_data.email,
                inviter_name=team_admin.username,
                token=invite_token,
                message_template=EmailService.team_invitation_message
            )
            EmailService.send_email(email_data)
            cls.logger().info(
                f"Team #{new_invite.team_id} invitation email sent to {new_invite.email}.")

        except exc.IntegrityError:
            db.session.rollback()
            cls.logger().error(
                f"Couldn't invite user {new_invite.email} to team #{new_invite.team_id}.")
            return UnsuccessfulTeamMessageResponse("Couldn't invite user to team.")
        else:
            return SuccessfulTeamMessageResponse("User invited.", TeamResponseStatus.INVITED.value)

    @classmethod
    def accept_invite(cls, invitation_data):
        user = Authenticator.authenticate(invitation_data)
        invite = db.session.query(TeamsInvitesTableEntry).filter(and_(
            TeamsInvitesTableEntry.team_id == invitation_data.team_id, TeamsInvitesTableEntry.email == user.email)) \
            .one_or_none()

        if not invite or invite.invite_token != invitation_data.invite_token:
            if db.session.query(UsersByTeamsTableEntry).filter(and_(
                    UsersByTeamsTableEntry.user_id == user.user_id,
                    UsersByTeamsTableEntry.team_id == invitation_data.team_id)
            ).one_or_none():
                return BadRequestTeamMessageResponse("You are already part of this team.",
                                                     TeamResponseStatus.ALREADY_REGISTERED.value)
            else:
                return BadRequestTeamMessageResponse("You weren't invited to this team.",
                                                     UserResponseStatus.WRONG_CREDENTIALS.value)

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
            cls.logger().info(f"User #{user.user_id} joined team #{invite.team_id}.")
        except exc.IntegrityError:
            db.session.rollback()
            cls.logger().error(f"User #{user.user_id} failed at joining team #{invite.team_id}.")
            return UnsuccessfulTeamMessageResponse("Couldn't join team.")
        else:
            return SuccessfulTeamMessageResponse("Team joined!", TeamResponseStatus.ADDED.value)

    @classmethod
    def team_users(cls, user_data):
        user = Authenticator.authenticate_team(user_data)

        team_users = db.session.query(
            UserTableEntry.user_id,
            UserTableEntry.username,
            UserTableEntry.email,
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
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "profile_pic": user.profile_pic,
                "online": user.online,
                "role": user.role
            }]

        return users

    @classmethod
    def team_channels(cls, user_data):
        user = Authenticator.authenticate_team(user_data)

        team_channels = db.session.query(ChannelTableEntry).filter(
            ChannelTableEntry.team_id == user.team_id
        ).all()

        cls.logger().info(f"User {user.username} got {len(team_channels)} users from team #{user_data.team_id}.")
        return SuccessfulChannelsListResponse(cls._team_channels_list(team_channels))

    @classmethod
    def _team_channels_list(cls, channels_list):
        channels = []

        for channel in channels_list:
            channels += [{
                "id": channel.channel_id,
                "name": channel.name,
                "creator": channel.creator,
                "visibility": channel.visibility,
                "description": channel.description,
                "welcome_message": channel.welcome_message
            }]

        return channels

    @classmethod
    def team_user_by_id(cls, user_data):
        user = Authenticator.authenticate_team(user_data.authentication)

        user_found = db.session.query(
            UserTableEntry.user_id,
            UserTableEntry.username,
            UserTableEntry.email,
            UserTableEntry.first_name,
            UserTableEntry.last_name,
            UserTableEntry.profile_pic,
            UserTableEntry.online,
            UsersByTeamsTableEntry.role
        ).join(
            UsersByTeamsTableEntry,
            and_(
                UserTableEntry.user_id == UsersByTeamsTableEntry.user_id,
                UserTableEntry.user_id == user_data.user_id,
                UsersByTeamsTableEntry.team_id == user.team_id
            )
        ).one_or_none()

        if not user_found:
            cls.logger().info(
                f"User {user.username} couldn't find user #{user_data.user_id} profile (in team {user.team_id}.")
            return NotFoundUserMessageResponse(
                f"User {user_data.user_id} not found!", UserResponseStatus.USER_NOT_FOUND.value)

        cls.logger().info(f"User {user.username} got user #{user_data.user_id} profile.")
        return SuccessfulUserResponse(user_found)

    @classmethod
    def delete_users(cls, delete_data):
        user = Authenticator.authenticate_team(delete_data.authentication, TeamRoles.is_team_admin)

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
                    return SuccessfulTeamMessageResponse("User removed!", TeamResponseStatus.REMOVED.value)
                except exc.IntegrityError:
                    db.session.rollback()
                    cls.logger().error(
                        f"User #{user.username} failed to delete user {delete_user.user_id} from team #{delete_user.team_id}.")
                    return UnsuccessfulTeamMessageResponse("Couldn't delete user.")
            else:
                cls.logger().info(
                    f"Cannot delete user #{delete_user.user_id} because he's role ({delete_user.role})" +
                    f" is higher than yours.")
                return ForbiddenTeamMessageResponse("You don't have enough permissions to delete this user.",
                                                    TeamResponseStatus.NOT_ENOUGH_PERMISSIONS.value)

        else:
            cls.logger().info(
                f"Trying to delete user #{delete_data.delete_id}, who's not part of the team" +
                f" {delete_data.authentication.team_id}.")
            return NotFoundTeamMessageResponse("Couldn't find user to delete", UserResponseStatus.USER_NOT_FOUND.value)

    @classmethod
    def change_role(cls, change_role_data):
        team_admin = Authenticator.authenticate_team(change_role_data.authentication, TeamRoles.is_team_creator)

        if change_role_data.new_role == TeamRoles.CREATOR.value:
            cls.logger().info(
                f"Trying to set user as team #{change_role_data.authentication.team_id} {TeamRoles.CREATOR.value}")
            return BadRequestTeamMessageResponse("You cannot set someone as team CREATOR.",
                                                 TeamResponseStatus.ROLE_UNAVAILABLE.value)

        user_team = db.session.query(UsersByTeamsTableEntry).filter(and_(
            UsersByTeamsTableEntry.user_id == change_role_data.user_id,
            UsersByTeamsTableEntry.team_id == change_role_data.authentication.team_id)
        ).one_or_none()

        if not user_team:
            cls.logger().info(
                f"Trying to modify role from user #{user_team.user_id}, who's not part of team #{user_team.team_id}")
            return BadRequestTeamMessageResponse("The given user is not part this team.",
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
            cls.logger().error(f"Failing to modifying role of #{user.user_id} in team #{user.team_id}.")
            return UnsuccessfulTeamMessageResponse("Couldn't modify user role.")
        else:
            return SuccessfulTeamMessageResponse("Role modified", TeamResponseStatus.ROLE_MODIFIED.value)

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
            return SuccessfulTeamMessageResponse("Team leaved!", TeamResponseStatus.REMOVED.value)
        except exc.IntegrityError:
            db.session.rollback()
            cls.logger().error(f"User #{user.user_id} failing to leave team #{user.team_id}.")
            return UnsuccessfulTeamMessageResponse("Couldn't leave team.")

    @classmethod
    def update_information(cls, update_data):
        user = Authenticator.authenticate_team(update_data.authentication, TeamRoles.is_team_admin)
        team = db.session.query(TeamTableEntry).filter(
            TeamTableEntry.team_id == update_data.authentication.team_id
        ).one_or_none()

        team.team_name = \
            update_data.updated_team["team_name"] if "team_name" in update_data.updated_team else team.team_name
        team.picture = \
            update_data.updated_team["picture"] if "picture" in update_data.updated_team else team.picture
        team.location = \
            update_data.updated_team["location"] if "location" in update_data.updated_team else team.location
        team.description = \
            update_data.updated_team["description"] if "description" in update_data.updated_team else team.description
        team.welcome_message = \
            update_data.updated_team["welcome_message"] if "welcome_message" in update_data.updated_team else team.welcome_message

        try:
            db.session.commit()
            cls.logger().info(
                f"Team {team.team_id} information updated by user {user.username}, who's team {user.role}.")
            return SuccessfulTeamResponse(team, TeamResponseStatus.UPDATED.value)
        except exc.IntegrityError:
            db.session.rollback()
            if db.session.query(TeamTableEntry).filter(
                    TeamTableEntry.team_name == update_data.updated_team.get("team_name")
            ).one_or_none():
                cls.logger().info(f"Trying to update team {update_data.authentication.team_id}'s name with " +
                                  f"{update_data.updated_team.get('team_name')}, that currently exists.")
                return BadRequestTeamMessageResponse(f"Name {update_data.updated_team.get('team_name')}" +
                                                     " is already in use!", TeamResponseStatus.ALREADY_REGISTERED.value)
            else:
                cls.logger().error(f"Couldn't update team {update_data.authentication.team_id} information.")
                return UnsuccessfulTeamMessageResponse("Couldn't update team information!")

    @classmethod
    def search_users(cls, user_data):
        user = Authenticator.authenticate_team(user_data.authentication)

        found_users = db.session.query(
            UserTableEntry
        ).join(
            UsersByTeamsTableEntry,
            and_(
                UsersByTeamsTableEntry.user_id == UserTableEntry.user_id,
                UsersByTeamsTableEntry.team_id == user_data.authentication.team_id,
                UserTableEntry.username.like(f"%{user_data.searched_username}%")
            )
        ).all()

        cls.logger().info(
            f"Found {len(found_users)} users for user #{user.user_id} with keyword {user.username} .")
        return SuccessfulUsersListResponse(cls._generate_users_list(found_users))

    @classmethod
    def _generate_users_list(cls, users_list):
        users = []

        for user in users_list:
            users += [{
                "id": user.user_id,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "profile_pic": user.profile_pic,
                "online": user.online
            }]

        return users

    @classmethod
    def delete_team(cls, user_data):
        user = Authenticator.authenticate_team(user_data, TeamRoles.is_team_admin)

        team_users = db.session.query(UsersByTeamsTableEntry)\
            .filter(UsersByTeamsTableEntry.team_id == user.team_id)

        team = db.session.query(TeamTableEntry).filter(TeamTableEntry.team_id == user.team_id).one_or_none()

        try:
            users = team_users.delete()
            db.session.flush()
            db.session.delete(team)
            db.session.commit()
            cls.logger().info(f"Team #{user.team_id} deleted, and {users} users-team relations released.")
            return SuccessfulTeamMessageResponse("Team removed!", TeamResponseStatus.REMOVED.value)
        except exc.IntegrityError:
            db.session.rollback()
            cls.logger().error(f"User #{user.user_id} couldn't remove team #{user.team_id}.")
            return UnsuccessfulTeamMessageResponse("Couldn't remove team.")

    @classmethod
    def add_forbidden_word(cls, word_data):
        user = Authenticator.authenticate_team(word_data.authentication, TeamRoles.is_team_admin)

        if db.session.query(ForbiddenWordsTableEntry).filter(
            ForbiddenWordsTableEntry.team_id == user.team_id,
            ForbiddenWordsTableEntry.word == word_data.word
        ).one_or_none():
            cls.logger().debug(f"User {user.username} attempted to add a forbidden word that already exists ({word_data.word}).")
            return BadRequestTeamMessageResponse("Word already forbidden!", TeamResponseStatus.ALREADY_REGISTERED.value)

        forbidden_word = ForbiddenWordsTableEntry(word=word_data.word, team_id=user.team_id)

        try:
            db.session.add(forbidden_word)
            db.session.commit()
            cls.logger().info(f"Word \"{word_data.word}\" forbidden in team #{user.team_id} by {user.username}.")
            return SuccessfulTeamMessageResponse("Forbidden word added!", TeamResponseStatus.ADDED.value)
        except exc.IntegrityError:
            db.session.rollback()
            cls.logger().error(f"User #{user.user_id} couldn't add forbidden word \"{word_data.word}\".")
            return UnsuccessfulTeamMessageResponse("Couldn't add forbidden word.")

    @classmethod
    def forbidden_words(cls, user_data):
        user = Authenticator.authenticate_team(user_data, TeamRoles.is_team_admin)

        forbidden_words = db.session.query(ForbiddenWordsTableEntry).filter(
                ForbiddenWordsTableEntry.team_id == user.team_id
        ).all()

        cls.logger().info(f"User {user.username} got {len(forbidden_words)} forbidden words in team #{user.team_id}.")
        return SuccessfulForbiddenWordsList(cls._generate_forbidden_words_list(forbidden_words))

    @classmethod
    def _generate_forbidden_words_list(cls, words_list):
        words = []

        for word in words_list:
            words += [{
                "id": word.id,
                "word": word.word
            }]

        return words

    @classmethod
    def delete_forbidden_word(cls, word_data):
        user = Authenticator.authenticate_team(word_data.authentication, TeamRoles.is_team_admin)

        forbidden_word = db.session.query(ForbiddenWordsTableEntry).filter(
            ForbiddenWordsTableEntry.team_id == user.team_id,
            ForbiddenWordsTableEntry.id == word_data.word_id
        ).one_or_none()

        if not forbidden_word:
            cls.logger().error(f"User {user.username} tried to delete forbidden word {word_data.word_id} from team "
                               f"#{user.team_id}, which doesn't exist.")
            return BadRequestTeamMessageResponse("Forbidden word not found!", TeamResponseStatus.NOT_FOUND.value)

        try:
            db.session.delete(forbidden_word)
            db.session.commit()
            cls.logger().info(f"User {user.username} deleted forbidden word \"{forbidden_word.word}\" from team "
                              f"#{user.team_id}.")
            return SuccessfulTeamMessageResponse("Forbidden word removed!", TeamResponseStatus.REMOVED.value)
        except exc.IntegrityError:
            db.session.rollback()
            cls.logger().error(f"User #{user.user_id} couldn't remove forbidden word \"{forbidden_word.word}\" "
                               f"from team #{user.team_id}.")
            return UnsuccessfulTeamMessageResponse("Couldn't remove team.")