from tables.users import UserTableEntry, PasswordRecoveryTableEntry
from dtos.models.users import User, PublicUser, PasswordRecovery, RegularClient


class UserDatabaseMapper:

    @classmethod
    def to_user(cls, user):
        return UserTableEntry(
            user_id=user.id,
            facebook_id=user.facebook_id,
            username=user.username,
            email=user.email,
            password=user.password,
            first_name=user.first_name,
            last_name=user.last_name,
            profile_pic=user.profile_pic,
            role=user.role,
            auth_token=user.token,
            online=user.online
        )

    @classmethod
    def to_password_recovery(cls, recovery):
        return PasswordRecoveryTableEntry(
            user_id=recovery.user_id,
            token=recovery.token
        )


class UserModelMapper:

    @classmethod
    def to_client(cls, client_entry):
        return RegularClient(
            client_id=client_entry.client_id
        ) if client_entry is not None else None

    @classmethod
    def to_user(cls, user_entry):
        return User(
            user_id=user_entry.user_id,
            role=user_entry.role,
            online=user_entry.online,
            token=user_entry.auth_token,
            first_name=user_entry.first_name,
            last_name=user_entry.last_name,
            profile_pic=user_entry.profile_pic,
            password=user_entry.password,
            email=user_entry.email,
            username=user_entry.username,
            facebook_id=user_entry.facebook_id
        ) if user_entry is not None else None

    @classmethod
    def to_users(cls, users_entries):
        users = []
        for user_entry in users_entries:
            user = PublicUser(
                user_id=user_entry.user_id,
                role=user_entry.role,
                online=user_entry.online,
                first_name=user_entry.first_name,
                last_name=user_entry.last_name,
                profile_pic=user_entry.profile_pic,
                email=user_entry.email,
                username=user_entry.username
            )
            user.facebook_id = user_entry.facebook_id
            users += [user]
        return users

    @classmethod
    def to_user_with_teams(cls, table_entries):
        user_with_teams = []
        for table_entry in table_entries:
            user = PublicUser(
                user_id=table_entry.user_id,
                username=table_entry.username,
                email=table_entry.email,
                first_name=table_entry.first_name,
                last_name=table_entry.last_name,
                profile_pic=table_entry.profile_pic,
                online=True,
                role=table_entry.user_role
            )
            user.team_id = table_entry.team_id
            user.team_name = table_entry.team_name
            user.team_picture = table_entry.picture
            user.team_location = table_entry.location
            user.team_description = table_entry.description
            user.team_message = table_entry.welcome_message
            user.team_role = table_entry.team_role
            user_with_teams += [user]
        return user_with_teams

    @classmethod
    def to_team_user(cls, table_entry):
        if table_entry is None:
            return None

        user = PublicUser(
            user_id=table_entry.user_id,
            username=table_entry.username,
            email=table_entry.email,
            first_name=table_entry.first_name,
            last_name=table_entry.last_name,
            profile_pic=table_entry.profile_pic,
            role=table_entry.user_role,
            online=table_entry.online
        )
        user.team_id = table_entry.team_id
        user.team_role = table_entry.team_role
        return user

    @classmethod
    def to_channel_user(cls, table_entry):
        if table_entry is None:
            return None

        user = PublicUser(
            user_id=table_entry.user_id,
            username=table_entry.username,
            email=table_entry.email,
            first_name=table_entry.first_name,
            last_name=table_entry.last_name,
            profile_pic=table_entry.profile_pic,
            online=table_entry.online,
            role=table_entry.role
        )
        user.team_id = table_entry.team_id
        user.channel_id = table_entry.channel_id
        user.is_channel_creator = table_entry.creator == table_entry.user_id
        return user

    @classmethod
    def to_password_recovery(cls, password_entry):
        return PasswordRecovery(
            user_id=password_entry.user_id,
            token=password_entry.token
        ) if password_entry is not None else None
