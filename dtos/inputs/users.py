class AuthenticationDTO:

    def __init__(self, username, token):
        self.username = username
        self.token = token


class NewUserDTO:

    def __init__(self, username, email, password, first_name, last_name, profile_pic):
        self.username = username
        self.email = email
        self.password = password
        self.first_name = first_name
        self.last_name = last_name
        self.profile_pic = profile_pic


class LoginDTO:

    def __init__(self, email, password):
        self.email = email
        self.password = password


class SearchUsersDTO:

    def __init__(self, username, token, searched_username):
        self.authentication = AuthenticationDTO(username, token)
        self.searched_username = searched_username
