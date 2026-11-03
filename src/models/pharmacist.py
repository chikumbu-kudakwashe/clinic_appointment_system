
from .staff import Staff


class Pharmacist(Staff):
    """Represents a pharmacist working at the clinic."""

    def role(self) -> str:
        return "Pharmacist"

    def fee(self) -> float:
        return 5
