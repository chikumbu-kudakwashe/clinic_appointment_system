
from contextlib import contextmanager
from src.models.appointment import Appointment, AppointmentStatus
from src.models.patient import Patient
from src.models.staff import Staff


class Clinic:
    """
    Clinic invariants:
    - All person and appointment IDs must be unique.
    - Patients and staff cannot have overlapping active appointments.
    - Every clinic action must be logged.
    - Internal collections must never be directly exposed.
    """

    def __init__(self, clock, log_file="clinic.log"):
        self.__patients = []
        self.__staff = []
        self.__appointments = []
        self.__ids = set()
        self.__clock = clock
        self.__log_file = log_file

    @contextmanager
    def __log_action(self, action):
        file = open(self.__log_file, "a", encoding="utf-8")
        print("[log] opened")

        try:
            yield file
        except Exception as error:
            file.write(f"FAILED {action}: {error}\n")
            raise
        finally:
            file.close()
            print("[log] closed")

    def register_patient(self, patient):
        with self.__log_action("register patient") as log:
            if not isinstance(patient, Patient):
                raise TypeError("A valid Patient is required.")

            if patient.id in self.__ids:
                raise ValueError("ID already exists.")

            self.__ids.add(patient.id)
            self.__patients.append(patient)
            log.write(f"Registered patient #{patient.id}\n")

    def register_staff(self, staff):
        with self.__log_action("register staff") as log:
            if not isinstance(staff, Staff):
                raise TypeError("A valid Staff member is required.")

            if staff.id in self.__ids:
                raise ValueError("ID already exists.")

            self.__ids.add(staff.id)
            self.__staff.append(staff)
            log.write(f"Registered staff #{staff.id}\n")

    def book_appointment(self, appointment_id, patient, staff, start_hour):
        with self.__log_action(f"book appointment #{appointment_id}") as log:

            if appointment_id in self.__ids:
                raise ValueError("Appointment ID already exists.")

            if patient not in self.__patients:
                raise ValueError("Patient is not registered.")

            if staff not in self.__staff:
                raise ValueError("Staff member is not registered.")

            if start_hour < self.__clock.now():
                raise ValueError("Cannot book an appointment in the past.")

            for appointment in self.__appointments:
                if (
                    appointment.status != AppointmentStatus.CANCELLED
                    and appointment.start_hour == start_hour
                    and (
                        appointment.patient == patient
                        or appointment.staff == staff
                    )
                ):
                    raise ValueError(
                        "Patient or staff member already has an appointment at this hour."
                    )

            appointment = Appointment(
                appointment_id, patient, staff, start_hour
            )

            self.__appointments.append(appointment)
            self.__ids.add(appointment_id)

            log.write(f"Booked appointment #{appointment_id}\n")

            return appointment

    def confirm_appointment(self, appointment_id):
        with self.__log_action(f"confirm appointment #{appointment_id}") as log:
            appointment = self.__find_appointment(appointment_id)
            appointment.confirm()

            log.write(f"Confirmed appointment #{appointment_id}\n")

    def cancel_appointment(self, appointment_id, reason=""):
        with self.__log_action(f"cancel appointment #{appointment_id}") as log:
            appointment = self.__find_appointment(appointment_id)
            appointment.cancel(self.__clock.now(), reason)

            log.write(
                f"Cancelled appointment #{appointment_id}: {reason}\n"
            )

    def show_staff_fees(self):
        with self.__log_action("show staff fees") as log:
            for staff in self.__staff:
                fee = staff.fee()
                print(staff.role(), fee)
                log.write(f"{staff.role()} fee: {fee}\n")

    def set_time(self, hour):
        with self.__log_action("set clinic time") as log:
            self.__clock.set_time(hour)
            log.write(f"Clinic time set to hour {hour}\n")

    def __find_appointment(self, appointment_id):
        for appointment in self.__appointments:
            if appointment.id == appointment_id:
                return appointment

        raise ValueError("Appointment not found.")

    @property
    def appointments(self):
        return tuple(self.__appointments)

    @property
    def patients(self):
        return tuple(self.__patients)

    @property
    def staff(self):
        return tuple(self.__staff)
