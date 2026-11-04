from src.errors import IllegalTransition
from src.policies.cancellation_policy import CancellationPolicy
from src.validation import require_positive_int

from .status import AppointmentStatus

S = AppointmentStatus
_LEGAL = {
    S.PENDING: {S.CONFIRMED, S.CANCELLED},
    S.CONFIRMED: {S.CANCELLED},
    S.CANCELLED: set(), 
}


# Invariants of Appointment:
#   lasts exactly one hour: [start_hour, start_hour + 1), start_hour in 0..167
#   id is a positive int; id, patient, staff and start_hour never change
#   status moves only PENDING->CONFIRMED, PENDING->CANCELLED, CONFIRMED->CANCELLED
#   CANCELLED is terminal
#   cancelling is refused once started, and for CONFIRMED with < 2 hours' notice
class Appointment:
    DURATION = 1

    def __init__(self, appointment_id, patient, staff, start_hour):
        self.__id = require_positive_int(appointment_id, "Appointment id")
        if isinstance(start_hour, bool) or not isinstance(start_hour, int):
            raise TypeError("Start hour must be an integer")
        if not 0 <= start_hour <= 167:
            raise ValueError("Start hour must be between 0 and 167")
        self.__patient = patient
        self.__staff = staff
        self.__start_hour = start_hour
        self.__status = S.PENDING
        self.__cancel_reason = ""

    id = property(lambda self: self.__id)
    patient = property(lambda self: self.__patient)
    staff = property(lambda self: self.__staff)
    start_hour = property(lambda self: self.__start_hour)
    status = property(lambda self: self.__status)
    cancel_reason = property(lambda self: self.__cancel_reason)

    @property
    def is_active(self):
        return self.__status is not S.CANCELLED

    def confirm(self):
        self.__move_to(S.CONFIRMED)

    def cancel(self, now, reason=""):
        problem = CancellationPolicy.violation(self.__status, self.__start_hour, now)
        if problem:
            raise IllegalTransition(problem)
        self.__move_to(S.CANCELLED)
        self.__cancel_reason = reason

    def __move_to(self, new_status):
        if new_status not in _LEGAL[self.__status]:
            raise IllegalTransition(
                f"{self.__status.value} -> {new_status.value} is not allowed"
            )
        self.__status = new_status
