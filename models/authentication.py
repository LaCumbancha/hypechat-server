import os, random, string


class AuthToken:
    _token_length = os.getenv('SECURITY_TOKEN_LENGTH')

    @classmethod
    def generate(cls):
        chars = string.ascii_letters + string.digits
        return "".join(random.choice(chars) for _ in range(int(cls._token_length)))
