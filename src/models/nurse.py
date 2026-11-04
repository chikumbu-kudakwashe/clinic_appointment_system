from src.validation import require_positive_int

from .staff import Staff


class Nurse(Staff):
    def __init__(self, name, person_id, p, **kwargs):
        super().__init__(name, person_id, **kwargs)
        self.__p = require_positive_int(p, "P")

    def role(self):
        return "Nurse"

    def fee(self):
        return 10 + (self.__p % 3)
