mock = None
EMPTY_DICTIONARY = {}
authentication_headers = {"X-Auth-Token": "test"}


class Header:

    def __init__(self, headers):
        self.headers = headers

    def to_list(self):
        return self.headers.items()

    def get(self, key):
        return self.headers.get(key)


class Request:

    def __init__(self, body=None, headers=None, args=None):
        self.body = body
        self.is_json = body is not None
        self.args = {} if args is None else args
        self.headers = Header(EMPTY_DICTIONARY if headers is None else headers)

    def get_json(self):
        return self.body

    def headers(self):
        return self.headers
