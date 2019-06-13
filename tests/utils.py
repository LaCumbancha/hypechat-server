EMPTY_DATA = None
EMPTY_DICTIONARY = {}


class Header:

    def __init__(self, headers):
        self.headers = headers

    def to_list(self):
        return self.headers.items()

    def get(self, key):
        return self.headers.get(key)


class Request:

    def __init__(self, json=None, headers=None):
        self.json = json
        self.is_json = json is not None
        self.headers = Header(EMPTY_DICTIONARY if headers is None else headers)

    def get_json(self):
        return self.json

    def headers(self):
        return self.headers
