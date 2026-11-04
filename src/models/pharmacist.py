from .staff import Staff


class Pharmacist(Staff):
    def role(self):
        return "Pharmacist"

    def fee(self):
        return 5
