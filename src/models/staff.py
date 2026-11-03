
from abc import abstractmethod
from .person import Person


class Staff(Person):
    """
    Abstract base class for clinic staff.

    Invariants:
    - Every staff member must have a valid name and ID.
    - Every staff member must implement a fee() method.
    """

    @abstractmethod
    def fee(self) -> float:
        """Return the consultation fee for this staff member."""
        pass
