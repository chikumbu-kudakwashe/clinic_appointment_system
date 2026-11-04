from src.validation import require_text

from .person import Person


class Lecturer(Person):
    def __init__(self, name, person_id, module, **kwargs):
        super().__init__(name, person_id, **kwargs)
        self.__module = require_text(module, "Module")

    @property
    def module(self):
        return self.__module

    def role(self):
        return "Lecturer"
