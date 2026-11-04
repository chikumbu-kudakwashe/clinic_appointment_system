import os
import sys
from contextlib import contextmanager

from src.errors import BookingError, ClinicError, LogUnavailable
from src.models.appointment import Appointment
from src.models.status import AppointmentStatus


# Invariants of Clinic:
#  every id (patient, staff, appointment) is unique across the whole clinic
#  no staff member and no patient has two non-cancelled appointments at one hour
#  (exception: an emergency patient may bump the staff member's PENDING one)
#  only registered people can be booked; nothing is booked in the past
#   every public action opens the log once, closes it once, and records
#     either its result or "FAILED <action>: <reason>"
#   internal collections are never handed out (only tuples)
class Clinic:
    def __init__(self, clock, log_path="logs/clinic.log"):
        self.__clock = clock
        self.__log_path = log_path
        self.__ids = set()
        self.__patients = {}
        self.__staff = {}
        self.__appointments = {}

    @contextmanager
    def __action(self, label):
        try:
            folder = os.path.dirname(self.__log_path)
            if folder:
                os.makedirs(folder, exist_ok=True)
            log = open(self.__log_path, "a", encoding="utf-8")
        except OSError as error:
            raise LogUnavailable(f"cannot open log: {error}") from error
        print("[log] opened")

        def note(message):
            try:
                log.write(message + "\n")
            except OSError as error:  
                print(f"[log] write failed: {error}", file=sys.stderr)

        try:
            yield note
        except Exception as error:
            note(f"FAILED {label}: {error}")
            raise
        finally:
            try:
                log.close()
            except OSError as error:
                print(f"[log] close failed: {error}", file=sys.stderr)
            print("[log] closed")

    # registration 
    def register_patient(self, patient):
        with self.__action(f"register patient #{patient.id}") as note:
            self.__claim_id(patient.id)
            self.__patients[patient.id] = patient
            note(f"Registered patient #{patient.id}")

    def register_staff(self, staff):
        with self.__action(f"register staff #{staff.id}") as note:
            self.__claim_id(staff.id)
            self.__staff[staff.id] = staff
            note(f"Registered staff #{staff.id} ({staff.role()})")

    def flag_emergency(self, patient_id, flag=True):
        with self.__action(f"flag emergency #{patient_id}") as note:
            self.__lookup(self.__patients, patient_id, "patient").set_emergency(flag)
            note(f"Patient #{patient_id} emergency={flag}")

    # appointments 
    def book_appointment(self, appointment_id, patient, staff, start_hour):
        with self.__action(f"book #{appointment_id}") as note:
            return self.__book(note, appointment_id, patient, staff, start_hour)

    def confirm_appointment(self, appointment_id):
        with self.__action(f"confirm #{appointment_id}") as note:
            self.__lookup(self.__appointments, appointment_id, "appointment").confirm()
            note(f"Confirmed #{appointment_id}")

    def cancel_appointment(self, appointment_id, reason=""):
        with self.__action(f"cancel #{appointment_id}") as note:
            appointment = self.__lookup(self.__appointments, appointment_id, "appointment")
            appointment.cancel(self.__clock.now(), reason)
            note(f"Cancelled #{appointment_id}: {reason}")

    def show_staff_fees(self):
        with self.__action("show fees") as note:
            for member in self.__staff.values():  # one loop, no type checks
                print(member.role(), member.fee())
                note(f"{member.role()} fee: {member.fee()}")

    # read-only views 
    @property
    def appointments(self):
        return tuple(self.__appointments.values())

    @property
    def patients(self):
        return tuple(self.__patients.values())

    @property
    def staff(self):
        return tuple(self.__staff.values())

    # internals 
    def __book(self, note, appointment_id, patient, staff, start_hour):
        self.__claim_id(appointment_id, check_only=True)
        if self.__patients.get(patient.id) is not patient:
            raise BookingError("patient is not registered")
        if self.__staff.get(staff.id) is not staff:
            raise BookingError("staff member is not registered")
        now = self.__clock.now()
        if start_hour <= now:
            raise BookingError("start hour is not in the future")

        same_hour = [a for a in self.__appointments.values()
                     if a.is_active and a.start_hour == start_hour]
        if any(a.patient is patient for a in same_hour):
            raise BookingError("patient already has an appointment at this hour")
        clashes = [a for a in same_hour if a.staff is staff]
        if clashes:
            if not patient.is_emergency:
                raise BookingError("staff member already booked at this hour")
            if any(a.status is AppointmentStatus.CONFIRMED for a in clashes):
                raise BookingError("cannot bump a CONFIRMED appointment")

        appointment = Appointment(appointment_id, patient, staff, start_hour)
        for old in clashes: 
            old.cancel(now, "bumped")
            note(f"Bumped #{old.id} for emergency patient #{patient.id}")
        self.__ids.add(appointment_id)
        self.__appointments[appointment_id] = appointment
        note(f"Booked #{appointment_id}: patient #{patient.id} with staff #{staff.id} at hour {start_hour}")
        return appointment

    def __claim_id(self, some_id, check_only=False):
        if some_id in self.__ids:
            raise BookingError(f"id {some_id} already in use")
        if not check_only:
            self.__ids.add(some_id)

    @staticmethod
    def __lookup(table, key, what):
        if key not in table:
            raise ClinicError(f"{what} #{key} not found")
        return table[key]
