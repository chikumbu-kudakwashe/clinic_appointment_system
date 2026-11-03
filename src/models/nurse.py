
from .staff import Staff


class Nurse(Staff):
    """
    Represents a nurse working at the clinic.
    """

    def __init__(self, name: str, person_id: int, p: int):
        super().__init__(name, person_id)
        self.__p = p

    def role(self) -> str:
        return "Nurse"

    def fee(self) -> float:
        return 10 + (self.__p % 3)
