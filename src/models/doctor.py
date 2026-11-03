
from .staff import Staff


class Doctor(Staff):
    """
    Represents a doctor working at the clinic.
    """

    def __init__(self, name: str, person_id: int, p: int):
        super().__init__(name, person_id)
        self.__p = p

    def role(self) -> str:
        return "Doctor"

    def fee(self) -> float:
        return 40 + 5 * (self.__p % 5)
