from .doctor import Doctor
from .lecturer import Lecturer


class MedicalLecturer(Doctor, Lecturer):
   
    def __init__(self, name, person_id, p, module):
        super().__init__(name, person_id, p, module=module)

    def role(self):
        return "Doctor and Lecturer"

    def fee(self):
        # Billing is clinical work, so the doctor's fee applies; lecturing has no fee.
        return Doctor.fee(self)
