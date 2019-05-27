from abc import ABC, abstractmethod


class Response(ABC):

    @abstractmethod
    def status_code(self):
        pass

    def cookies(self):
        return None
