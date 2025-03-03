from abc import ABC


class Printable(ABC):
    """ An abstract base class that implements printing functionality. """

    def __repr__(self):
        return str(self.__dict__)
