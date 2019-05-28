from abc import ABC, abstractmethod


class Response(ABC):

    @abstractmethod
    def status_code(self):
        pass

    def headers(self):
        return None
