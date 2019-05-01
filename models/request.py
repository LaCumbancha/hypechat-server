class ClientRequest:

    def __init__(self, data):
        self.data = data

    def token(self):
        return self.data.get_json()["auth_token"]

    def username(self):
        return self.data.get_json()["username"]

    def email(self):
        return self.data.get_json()["email"]

    def password(self):
        return self.data.get_json()["password"]
