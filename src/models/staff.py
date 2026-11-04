from abc import abstractmethod

from .person import Person


# Invariants of Staff: everything Person guarantees, plus a fee() for every subclass.
class Staff(Person):
    @abstractmethod
    def fee(self):
        ...
