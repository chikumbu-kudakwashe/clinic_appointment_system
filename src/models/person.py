
from abc import ABC, abstractmethod


class Person(ABC):
    """
    Abstract base class representing a person in the clinic.

    Invariants:
    - Name must not be empty.
    - ID must be a positive integer.
    - Internal fields must not be directly exposed.
    """

    def __init__(self, name: str, person_id: int):
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Person name cannot be empty.")

        if isinstance(person_id, bool) or not isinstance(person_id, int):
            raise TypeError("Person ID must be an integer.")

        if person_id <= 0:
            raise ValueError("Person ID must be positive.")

        self.__name = name.strip()
        self.__id = person_id

    @property
    def name(self):
        return self.__name

    @property
    def id(self):
        return self.__id

    @abstractmethod
    def role(self) -> str:
        """Return the role of this person."""
        pass

