
from .person import Person


class Patient(Person):
    """
    Represents a patient registered at the clinic.
    """

    def __init__(self, name: str, person_id: int):
        super().__init__(name, person_id)

    def role(self) -> str:
        return "Patient"

