from .person import Person


class Patient(Person):
    def __init__(self, name, person_id, **kwargs):
        super().__init__(name, person_id, **kwargs)
        self.__emergency = False

    @property
    def is_emergency(self):
        return self.__emergency

    def set_emergency(self, flag=True):
        self.__emergency = bool(flag)

    def role(self):
        return "Patient"
