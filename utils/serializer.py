from abc import ABC, abstractmethod


class Jsonizable(ABC):

    @abstractmethod
    def json(self):
        pass
