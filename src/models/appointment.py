
from enum import Enum


class AppointmentStatus(Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"


class Appointment:
    """
    Appointment invariants:
    - Every appointment lasts exactly one hour.
    - A cancelled appointment can never be reactivated.
    - A confirmed appointment cannot be cancelled less than
      two hours before its start time.
    - No appointment can be cancelled after it has started.
    """

    def __init__(self, appointment_id, patient, staff, start_hour):

        if isinstance(appointment_id, bool) or not isinstance(appointment_id, int):
            raise TypeError("Appointment ID must be an integer.")

        if appointment_id <= 0:
            raise ValueError("Appointment ID must be positive.")

        if isinstance(start_hour, bool) or not isinstance(start_hour, int):
            raise TypeError("Start hour must be an integer.")

        if not 0 <= start_hour <= 167:
            raise ValueError("Start hour must be between 0 and 167.")

        from .patient import Patient
        from .staff import Staff

        if not isinstance(patient, Patient):
            raise TypeError("Appointment requires a valid Patient.")

        if not isinstance(staff, Staff):
            raise TypeError("Appointment requires a valid Staff member.")

        self.__id = appointment_id
        self.__patient = patient
        self.__staff = staff
        self.__start_hour = start_hour
        self.__status = AppointmentStatus.PENDING

    @property
    def id(self):
        return self.__id

    @property
    def patient(self):
        return self.__patient

    @property
    def staff(self):
        return self.__staff

    @property
    def start_hour(self):
        return self.__start_hour

    @property
    def status(self):
        return self.__status

    def confirm(self):
        if self.__status == AppointmentStatus.CANCELLED:
            raise ValueError("Cancelled appointments cannot be confirmed.")

        if self.__status == AppointmentStatus.CONFIRMED:
            raise ValueError("Appointment is already confirmed.")

        self.__status = AppointmentStatus.CONFIRMED

    def cancel(self, current_hour, reason=""):
        if isinstance(current_hour, bool) or not isinstance(current_hour, int):
            raise TypeError("Current hour must be an integer.")

        if not 0 <= current_hour <= 168:
            raise ValueError("Current hour must be between 0 and 168.")

        if self.__status == AppointmentStatus.CANCELLED:
            raise ValueError("Appointment is already cancelled.")

        if current_hour >= self.__start_hour:
            raise ValueError("Cannot cancel an appointment that has started.")

        if (
            self.__status == AppointmentStatus.CONFIRMED
            and self.__start_hour - current_hour < 2
        ):
            raise ValueError("Confirmed appointments need at least 2 hours' notice.")

        self.__status = AppointmentStatus.CANCELLED
