from daos.database import DatabaseClient
from daos.users import UserDatabaseClient
from daos.teams import TeamDatabaseClient
from daos.channels import ChannelDatabaseClient

from dtos.responses.clients import *
from dtos.responses.teams import *
from dtos.responses.channels import *
from dtos.models.users import *
from dtos.model import *

from services.emails import EmailService
from services.facebook import FacebookService

from exceptions.exceptions import *
from models.authentication import Authenticator

from passlib.apps import custom_app_context as hashing
from sqlalchemy.exc import IntegrityError

import logging


class UserService:

    @classmethod
    def logger(cls):
        return logging.getLogger(cls.__name__)

    @classmethod
    def create_user(cls, user_data):

        try:
            new_client = UserDatabaseClient.add_client()
            new_user = User(
                user_id=new_client.id,
                username=user_data.username,
                email=user_data.email,
                password=hashing.hash(user_data.password),
                first_name=user_data.first_name,
                last_name=user_data.last_name,
                profile_pic=user_data.profile_pic,
                role=user_data.role or UserRoles.USER.value,
                token=Authenticator.generate(new_client.id, user_data.password)
            )
            UserDatabaseClient.add_user(new_user)
            DatabaseClient.commit()
            cls.logger().info(f"User #{new_client.id} created.")
            headers = {"auth_token": new_user.token}
            return SuccessfulUserResponse(new_user, headers)

        except IntegrityError as exc:
            DatabaseClient.rollback()
            if UserDatabaseClient.get_user_by_email(user_data.email) is not None:
                cls.logger().info(f"Failing to create user {user_data.username}. Email already in use.", exc)
                return BadRequestUserMessageResponse("Email already in use for other user.",
                                                     UserResponseStatus.ALREADY_REGISTERED.value)
            elif UserDatabaseClient.get_user_by_username(user_data.username) is not None:
                cls.logger().info(f"Failing to create user #{user_data.username}. Username already in use.", exc)
                return BadRequestUserMessageResponse("Username already in use for other user.",
                                                     UserResponseStatus.ALREADY_REGISTERED.value)
            else:
                cls.logger().info(f"Failing to create user #{user_data.username}.")
                return UnsuccessfulClientResponse("Couldn't create user.")
        except:
            DatabaseClient.rollback()
            cls.logger().info(f"Failing to create user #{user_data.username}.")
            return UnsuccessfulClientResponse("Couldn't create user.")

    @classmethod
    def login_user(cls, user_data):
        if user_data.facebook_token is None:
            return cls._login_app_user(user_data)
        else:
            return cls._login_facebook_user(user_data)

    @classmethod
    def _login_app_user(cls, user_data):
        user = UserDatabaseClient.get_user_by_email(user_data.email)

        if user:
            if hashing.verify(user_data.password, user.password):
                cls.logger().debug(f"Generating token for user {user.id}")
                user.token = Authenticator.generate(user.id, user_data.password)
                user.online = True
                UserDatabaseClient.update_user(user)
                DatabaseClient.commit()
                cls.logger().info(f"User #{user.id} logged in")
                headers = {"auth_token": user.token}
                return SuccessfulUserResponse(user, headers)
            else:
                cls.logger().info(f"Wrong credentials while attempting to log in user #{user_data.email}")
                return SuccessfulUserMessageResponse("Wrong email or password.",
                                                     UserResponseStatus.WRONG_CREDENTIALS.value)
        else:
            cls.logger().info(f"User #{user_data.email} not found.")
            raise UserNotFoundError("User not found.", UserResponseStatus.USER_NOT_FOUND.value)

    @classmethod
    def _login_facebook_user(cls, user_data):
        try:
            facebook_user = FacebookService.get_user_from_facebook(user_data)
            user = UserDatabaseClient.get_user_by_facebook_id(facebook_user.facebook_id)

            if user is not None:
                cls.logger().info(f"Logging in Facebook user with Facebook ID #{facebook_user.facebook_id}.")
                cls.logger().debug(f"Generating token for user {user.id}")
                user.token = Authenticator.generate(user.id)
                user.online = True
                UserDatabaseClient.update_user(user)
                DatabaseClient.commit()
                cls.logger().info(f"User #{user.id} logged in.")
                headers = {"auth_token": user.token}
                return SuccessfulUserResponse(user, headers)
            else:
                cls.logger().info(f"Creating new Facebook user with Facebook ID #{facebook_user.facebook_id}.")
                new_client = UserDatabaseClient.add_client()
                new_user = User(
                    user_id=new_client.id,
                    facebook_id=facebook_user.facebook_id,
                    email=facebook_user.email,
                    first_name=facebook_user.first_name,
                    last_name=facebook_user.last_name,
                    profile_pic=facebook_user.profile_pic,
                    role=UserRoles.USER.value,
                    token=Authenticator.generate(new_client.id)
                )
                UserDatabaseClient.add_user(new_user)
                DatabaseClient.commit()
                cls.logger().info(f"User #{new_client.id} logged in.")
                headers = {"auth_token": new_user.token}
                return SuccessfulUserResponse(new_user, headers)
        except FacebookWrongTokenError:
            cls.logger().info(f"Failing to logging in user with Facebook token #{user_data.facebook_token}.")
            return UnsuccessfulClientResponse("Couldn't perform login.")

    @classmethod
    def logout_user(cls, user_data):
        user = Authenticator.authenticate(user_data)
        user.token = None
        user.online = False
        UserDatabaseClient.update_user(user)
        DatabaseClient.commit()
        cls.logger().info(f"User #{user.id} logged out.")
        return SuccessfulUserMessageResponse("User logged out.", UserResponseStatus.LOGGED_OUT.value)

    @classmethod
    def set_user_online(cls, user_data):
        user = Authenticator.authenticate(user_data)
        user.online = True
        UserDatabaseClient.update_user(user)
        DatabaseClient.commit()
        cls.logger().info(f"User #{user.id} set online.")
        return SuccessfulUserResponse(user)

    @classmethod
    def set_user_offline(cls, user_data):
        user = Authenticator.authenticate(user_data)
        user.online = False
        UserDatabaseClient.update_user(user)
        DatabaseClient.commit()
        cls.logger().info(f"User #{user.id} set offline.")
        return SuccessfulUserResponse(user)

    @classmethod
    def teams_for_user(cls, user_data):
        user = Authenticator.authenticate(user_data)
        teams = TeamDatabaseClient.get_user_teams_by_user_id(user.id, user.role == UserRoles.ADMIN.value)

        return SuccessfulTeamsListResponse(cls._generate_teams_list(teams))

    @classmethod
    def _generate_teams_list(cls, teams_list):
        teams = []

        for team in teams_list:
            teams += [{
                "id": team.id,
                "team_name": team.name,
                "picture": team.picture,
                "location": team.location,
                "description": team.description,
                "welcome_message": team.welcome_message,
                "role": team.role
            }]

        return teams

    @classmethod
    def channels_for_user(cls, user_data):
        user = Authenticator.authenticate_team(user_data)
        channels = ChannelDatabaseClient.get_user_channels_by_user_id(user.id, user.team_id,
                                                                      user.role == UserRoles.ADMIN.value)

        return SuccessfulChannelsListResponse(cls._generate_channels_list(channels))

    @classmethod
    def _generate_channels_list(cls, channels_list):
        channels = []

        for channel in channels_list:
            channels += [{
                "channel_id": channel.channel_id,
                "name": channel.name,
                "creator": {
                    "id": channel.creator.id,
                    "username": channel.creator.username,
                    "first_name": channel.creator.first_name,
                    "last_name": channel.creator.last_name
                },
                "visibility": channel.visibility,
                "description": channel.description,
                "welcome_message": channel.welcome_message
            }]

        return channels

    @classmethod
    def update_user(cls, update_data):
        user = Authenticator.authenticate(update_data)

        user.username = \
            update_data.updated_user["username"] if "username" in update_data.updated_user else user.username
        user.email = \
            update_data.updated_user["email"] if "email" in update_data.updated_user else user.email
        user.password = \
            hashing.hash(
                update_data.updated_user["password"]) if "password" in update_data.updated_user else user.password
        user.first_name = \
            update_data.updated_user["first_name"] if "first_name" in update_data.updated_user else user.first_name
        user.last_name = \
            update_data.updated_user["last_name"] if "last_name" in update_data.updated_user else user.last_name
        user.profile_pic = \
            update_data.updated_user["profile_pic"] if "profile_pic" in update_data.updated_user else user.profile_pic

        try:
            UserDatabaseClient.update_user(user)
            DatabaseClient.commit()
            cls.logger().info(f"User {user.id} information updated.")
            return SuccessfulUserResponse(user)
        except IntegrityError:
            DatabaseClient.rollback()
            new_username = update_data.updated_user.get("username")
            new_email = update_data.updated_user.get("email")

            if UserDatabaseClient.get_user_by_username(new_username) is not None:
                cls.logger().info(f"Name {new_email} is taken for another user.")
                return BadRequestUserMessageResponse(f"Name {new_username} is already in use!",
                                                     UserResponseStatus.ALREADY_REGISTERED.value)
            elif UserDatabaseClient.get_user_by_email(new_email) is not None:
                cls.logger().info(f"Email {new_email} is taken for another user.")
                return BadRequestUserMessageResponse(f"Email {new_email} is already in use!",
                                                     UserResponseStatus.ALREADY_REGISTERED.value)
            else:
                cls.logger().error(f"Couldn't update user {user.id} information.")
                return UnsuccessfulClientResponse("Couldn't update user information!")

    @classmethod
    def user_profile(cls, user_data):
        user = Authenticator.authenticate(user_data)
        has_teams = len(TeamDatabaseClient.get_user_teams_by_user_id(user.id))
        profile = UserDatabaseClient.get_user_profile(user)
        cls.logger().info(f"Retrieved user {user.username} profile.")
        return SuccessfulFullUserResponse(cls._generate_user_profile(profile, has_teams))

    @classmethod
    def _generate_user_profile(cls, full_user, has_teams):
        teams = []
        user_data = full_user

        if has_teams:

            for team in full_user:
                teams += [{
                    "id": team.team_id,
                    "name": team.team_name,
                    "location": team.team_location,
                    "picture": team.team_picture,
                    "description": team.team_description,
                    "welcome_message": team.team_welcome,
                    "role": team.team_role,
                    "messages": team.team_messages
                }]

            user_data = full_user[0]

        return {
            "id": user_data.id,
            "username": user_data.username,
            "email": user_data.email,
            "first_name": user_data.first_name,
            "last_name": user_data.last_name,
            "profile_pic": user_data.profile_pic,
            "created": user_data.created,
            "role": user_data.role,
            "teams": teams
        }

    @classmethod
    def recover_password(cls, recover_data):
        user = UserDatabaseClient.get_user_by_email(recover_data.email)

        if user is not None:
            old_password_recovery = UserDatabaseClient.get_password_recovery_by_id(user.id)

            if old_password_recovery is not None:
                cls.logger().debug(f"It already exists a recovery token for user {user.username}. Resending token.")
                recovery_token = old_password_recovery.token

            else:
                recovery_token = Authenticator.generate_recovery_token()
                cls.logger().debug("Generating recovery token")
                password_recovery = PasswordRecovery(user_id=user.id, token=recovery_token)
                UserDatabaseClient.add_password_recovery(password_recovery)
                DatabaseClient.commit()

            email_data = RecoveryPasswordEmailDTO(
                email=user.email,
                username=user.username,
                token=recovery_token,
                message_template=EmailService.recovery_token_message
            )
            EmailService.send_email(email_data)

            cls.logger().info(f"Sending recovery token email for user {user.username}.")
            return SuccessfulUserMessageResponse("Recovery token sent!", UserResponseStatus.OK.value)

        else:
            cls.logger().info(f"User {recover_data.email} not found.")
            raise UserNotFoundError("User not found.", UserResponseStatus.USER_NOT_FOUND.value)

    @classmethod
    def regenerate_token(cls, regenerate_data):
        user = UserDatabaseClient.get_user_by_email(regenerate_data.email)

        if user:
            password_recovery = UserDatabaseClient.get_password_recovery_by_id(user.id)

            if password_recovery:
                try:
                    UserDatabaseClient.delete_password_recovery(password_recovery)
                    cls.logger().debug(f"Deleting token recover entry for user {user.id}")
                    user.token = Authenticator.generate(user.id)
                    cls.logger().debug(f"Regenerating token for user {user.id}")
                    user.online = True
                    UserDatabaseClient.update_user(user)
                    DatabaseClient.commit()
                    cls.logger().info(f"Logging in user {user.id}")
                    headers = {"auth_token": user.token}
                    return SuccessfulUserResponse(user, headers)
                except IntegrityError:
                    DatabaseClient.rollback()
                    cls.logger().error(f"Couldn't regenerate token for user #{user.id}.")
                    return UnsuccessfulClientResponse("Couldn't regenerate token.")
            else:
                cls.logger().info(f"Attempting to recover password for user #{user.id} with no password recovery token.")
                return BadRequestUserMessageResponse("You haven't ask for password recovery!",
                                                     UserResponseStatus.WRONG_CREDENTIALS.value)
        else:
            cls.logger().info(f"User {regenerate_data.email} not found.")
            raise UserNotFoundError("User not found.", UserResponseStatus.USER_NOT_FOUND.value)

    @classmethod
    def get_all_users(cls, user_data):
        admin = Authenticator.authenticate(user_data, UserRoles.is_admin)
        users = UserDatabaseClient.get_all_users()
        cls.logger().info(f"Admin {admin.id} retrieved {len(users)} users.")
        return SuccessfulUsersListResponse(list(map(lambda user: user.__dict__, users)))
