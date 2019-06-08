from app import db
from dtos.responses.clients import *
from dtos.responses.teams import *
from dtos.model import *
from exceptions.exceptions import *
from models.authentication import Authenticator
from services.emails import EmailService
from tables.users import *
from tables.teams import *
from passlib.apps import custom_app_context as hashing
from sqlalchemy import exc, and_, literal

import logging


class UserService:

    @classmethod
    def logger(cls):
        return logging.getLogger(cls.__name__)

    @classmethod
    def create_user(cls, user_data):
        new_client = ClientTableEntry()

        try:
            db.session.add(new_client)
            db.session.flush()
            new_user = UserTableEntry(
                user_id=new_client.client_id,
                username=user_data.username,
                email=user_data.email,
                password=hashing.hash(user_data.password),
                first_name=user_data.first_name,
                last_name=user_data.last_name,
                profile_pic=user_data.profile_pic,
                role=user_data.role or UserRoles.USER.value,
                auth_token=Authenticator.generate(user_data.username, user_data.password),
                online=True
            )
            db.session.add(new_user)
            db.session.flush()
            db.session.commit()
            cls.logger().info(f"User #{new_client.client_id} created.")
        except exc.IntegrityError:
            db.session.rollback()
            if db.session.query(UserTableEntry).filter(UserTableEntry.email == user_data.email).one_or_none():
                cls.logger().info(
                    f"Failing to create user {new_client.client_id}. Email already in use for other user.")
                return BadRequestUserMessageResponse("Email already in use for other user.",
                                                     UserResponseStatus.ALREADY_REGISTERED.value)
            elif db.session.query(UserTableEntry).filter(
                    UserTableEntry.username == user_data.username).one_or_none():
                cls.logger().info(
                    f"Failing to create user #{new_client.client_id}. Username already in use for other user.")
                return BadRequestUserMessageResponse("Username already in use for other user.",
                                                     UserResponseStatus.ALREADY_REGISTERED.value)
            else:
                cls.logger().info(f"Failing to create user #{new_client.client_id}.")
                return UnsuccessfulClientResponse("Couldn't create user.")
        else:
            headers = {
                "username": new_user.username,
                "auth_token": new_user.auth_token
            }
            return SuccessfulUserResponse(new_user, headers)

    @classmethod
    def login_user(cls, user_data):
        user = db.session.query(UserTableEntry).filter(
            UserTableEntry.email == user_data.email).one_or_none()

        if user:
            if hashing.verify(user_data.password, user.password):
                cls.logger().debug(f"Generating token for user {user.user_id}")
                user.auth_token = Authenticator.generate(user.username, user_data.password)
                user.online = True
                db.session.commit()
                cls.logger().info(f"Logging in user {user.user_id}")
                headers = {
                    "username": user.username,
                    "auth_token": user.auth_token
                }
                return SuccessfulUserResponse(user, headers)
            else:
                cls.logger().info(f"Wrong credentials while attempting to log in user #{user_data.email}")
                return SuccessfulUserMessageResponse("Wrong email or password.",
                                                     UserResponseStatus.WRONG_CREDENTIALS.value)
        else:
            cls.logger().info(f"User #{user_data.email} not found.")
            raise UserNotFoundError("User not found.", UserResponseStatus.USER_NOT_FOUND.value)

    @classmethod
    def logout_user(cls, user_data):
        user = Authenticator.authenticate(user_data)
        user.auth_token = None
        db.session.commit()
        cls.logger().info(f"User #{user.user_id} logged out.")
        return SuccessfulUserMessageResponse("User logged out.", UserResponseStatus.LOGGED_OUT.value)

    @classmethod
    def set_user_online(cls, user_data):
        user = Authenticator.authenticate(user_data)
        user.online = True
        db.session.commit()
        cls.logger().info(f"User #{user.user_id} set online.")
        return SuccessfulUserResponse(user)

    @classmethod
    def set_user_offline(cls, user_data):
        user = Authenticator.authenticate(user_data)
        user.online = False
        db.session.commit()
        cls.logger().info(f"User #{user.user_id} set offline.")
        return SuccessfulUserResponse(user)

    @classmethod
    def teams_for_user(cls, user_data):
        user = Authenticator.authenticate(user_data)

        if user.role == UserRoles.ADMIN.value:
            teams = db.session.query(
                TeamTableEntry.team_id,
                TeamTableEntry.team_name,
                TeamTableEntry.picture,
                TeamTableEntry.location,
                TeamTableEntry.description,
                TeamTableEntry.welcome_message,
                literal(None).label("role")
            ).all()

        else:
            teams = db.session.query(
                TeamTableEntry.team_id,
                TeamTableEntry.team_name,
                TeamTableEntry.picture,
                TeamTableEntry.location,
                TeamTableEntry.description,
                TeamTableEntry.welcome_message,
                UsersByTeamsTableEntry.role
            ).join(
                UsersByTeamsTableEntry,
                and_(
                    UsersByTeamsTableEntry.user_id == user.user_id,
                    UsersByTeamsTableEntry.team_id == TeamTableEntry.team_id
                )
            ).all()

        return SuccessfulTeamsListResponse(cls._generate_teams_list(teams))

    @classmethod
    def _generate_teams_list(cls, teams_list):
        teams = []

        for team in teams_list:
            teams += [{
                "id": team.team_id,
                "team_name": team.team_name,
                "picture": team.picture,
                "location": team.location,
                "description": team.description,
                "welcome_message": team.welcome_message,
                "role": team.role
            }]

        return teams

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
            db.session.commit()
            cls.logger().info(
                f"User {user.user_id} information updated.")
            return SuccessfulUserResponse(user)
        except exc.IntegrityError:
            db.session.rollback()
            if db.session.query(UserTableEntry).filter(
                    UserTableEntry.username == update_data.updated_user.get("username")
            ).one_or_none():
                cls.logger().info(f"Name {update_data.updated_user.get('username')} is taken for another user.")
                return BadRequestUserMessageResponse(f"Name {update_data.updated_user.get('username')}" +
                                                     " is already in use!", UserResponseStatus.ALREADY_REGISTERED.value)
            elif db.session.query(UserTableEntry).filter(
                    UserTableEntry.email == update_data.updated_user.get("email")
            ).one_or_none():
                cls.logger().info(f"Email {update_data.updated_user.get('email')} is taken for another user.")
                return BadRequestUserMessageResponse(f"Email {update_data.updated_user.get('email')}" +
                                                     " is already in use!", UserResponseStatus.ALREADY_REGISTERED.value)
            else:
                cls.logger().error(f"Couldn't update user {user.user_id} information.")
                return UnsuccessfulUserMessageResponse("Couldn't update user information!")

    @classmethod
    def user_profile(cls, user_data):
        user = Authenticator.authenticate(user_data)

        has_teams = len(db.session.query(UsersByTeamsTableEntry).filter(
            UsersByTeamsTableEntry.user_id == user.user_id
        ).all()) > 0

        if has_teams:
            full_user = db.session.query(
                UserTableEntry.user_id,
                UserTableEntry.username,
                UserTableEntry.email,
                UserTableEntry.first_name,
                UserTableEntry.last_name,
                UserTableEntry.profile_pic,
                UserTableEntry.role,
                TeamTableEntry.team_id,
                TeamTableEntry.team_name,
                TeamTableEntry.picture,
                TeamTableEntry.location,
                TeamTableEntry.description,
                TeamTableEntry.welcome_message,
                UsersByTeamsTableEntry.role
            ).join(
                UsersByTeamsTableEntry,
                UsersByTeamsTableEntry.user_id == UserTableEntry.user_id
            ).join(
                TeamTableEntry,
                UsersByTeamsTableEntry.team_id == TeamTableEntry.team_id
            ).filter(
                UserTableEntry.user_id == user.user_id
            ).all()

            cls.logger().info(f"Retrieved user {user.username} profile.")
            return SuccessfulFullUserResponse(cls._generate_full_user(full_user, has_teams))
        else:
            cls.logger().info(f"Retrieved user {user.username} profile.")
            return SuccessfulFullUserResponse(cls._generate_full_user(user, has_teams))

    @classmethod
    def _generate_full_user(cls, full_user, has_teams):
        teams = []
        user_data = full_user

        if has_teams:

            for team in full_user:
                teams += [{
                    "id": team.team_id,
                    "name": team.team_name,
                    "location": team.location,
                    "picture": team.picture,
                    "description": team.description,
                    "welcome_message": team.welcome_message,
                    "role": team.role
                }]

            user_data = full_user[0]

        return {
            "id": user_data.user_id,
            "username": user_data.username,
            "email": user_data.email,
            "first_name": user_data.first_name,
            "last_name": user_data.last_name,
            "profile_pic": user_data.profile_pic,
            "role": user_data.role,
            "teams": teams
        }

    @classmethod
    def recover_password(cls, recover_data):
        user = db.session.query(UserTableEntry).filter(
            UserTableEntry.email == recover_data.email
        ).one_or_none()

        if user:
            old_password_recovery = db.session.query(PasswordRecoveryTableEntry).filter(
                PasswordRecoveryTableEntry.user_id == user.user_id
            ).one_or_none()

            if old_password_recovery:
                cls.logger().debug(f"It already exists a recovery token for user {user.username}. Resending token.")
                recovery_token = old_password_recovery.token

            else:
                recovery_token = Authenticator.generate_recovery()
                cls.logger().debug("Generating recovery token")
                password_recovery = PasswordRecoveryTableEntry(user_id=user.user_id, token=recovery_token)
                db.session.add(password_recovery)
                db.session.commit()

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
            cls.logger().info(f"User {regenerate_data.email} not found.")
            raise UserNotFoundError("User not found.", UserResponseStatus.USER_NOT_FOUND.value)

    @classmethod
    def regenerate_token(cls, regenerate_data):
        user = db.session.query(UserTableEntry).filter(
            UserTableEntry.email == regenerate_data.email
        ).one_or_none()

        if user:
            password_recovery = db.session.query(PasswordRecoveryTableEntry).filter(
                PasswordRecoveryTableEntry.user_id == user.user_id
            ).one_or_none()

            if password_recovery:
                try:
                    db.session.delete(password_recovery)
                    db.session.flush()
                    cls.logger().debug(f"Deleting token recover entry for user {user.user_id}")
                    user.auth_token = Authenticator.generate(user.username, None)
                    cls.logger().debug(f"Regenerating token for user {user.user_id}")
                    user.online = True
                    db.session.commit()
                    cls.logger().info(f"Logging in user {user.user_id}")
                    headers = {
                        "username": user.username,
                        "auth_token": user.auth_token
                    }
                    return SuccessfulUserResponse(user, headers)
                except exc.IntegrityError:
                    cls.logger().error(f"Couldn't regenerate token for user #{user.user_id}.")
                    raise UnsuccessfulClientResponse("Couldn't regenerate token.")
            else:
                cls.logger().info(
                    f"Attempting to recover password for user #{user.user_id} with no password recovery token.")
                return BadRequestUserMessageResponse("You haven't ask for password recovery!",
                                                     UserResponseStatus.WRONG_CREDENTIALS.value)

        else:
            cls.logger().info(f"User {regenerate_data.email} not found.")
            raise UserNotFoundError("User not found.", UserResponseStatus.USER_NOT_FOUND.value)
