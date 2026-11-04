from abc import ABC, abstractmethod

from src.validation import require_positive_int, require_text


# Invariants of Person:
#   name is a non-empty, non-blank string (stored stripped)
#   id is a positive int (bool is rejected)
#   fields are private; only read-only properties are exposed
class Person(ABC):
    __constructed = 0  

    def __init__(self, name, person_id, **kwargs):
        super().__init__(**kwargs)
        self.__name = require_text(name, "Name")
        self.__id = require_positive_int(person_id, "Person id")
        Person.__constructed += 1

    @classmethod
    def constructed_count(cls):
        return Person.__constructed

    @property
    def name(self):
        return self.__name

    @property
    def id(self):
        return self.__id

    @abstractmethod
    def role(self):
        ...
