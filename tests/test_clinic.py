import contextlib
import io
import os
import tempfile
import unittest

from src.core.clinic import Clinic
from src.core.clock import Clock
from src.errors import BookingError, ClinicError, IllegalTransition, LogUnavailable
from src.models.appointment import Appointment
from src.models.doctor import Doctor
from src.models.lecturer import Lecturer
from src.models.medical_lecturer import MedicalLecturer
from src.models.nurse import Nurse
from src.models.patient import Patient
from src.models.person import Person
from src.models.pharmacist import Pharmacist
from src.models.staff import Staff
from src.models.status import AppointmentStatus as S


def quiet(func, *args, **kwargs):
  
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        result = func(*args, **kwargs)
    return result, buffer.getvalue()


class ClinicTestCase(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.log_path = os.path.join(tmp.name, "clinic.log")
        self.clock = Clock(0)
        self.clinic = Clinic(self.clock, self.log_path)
        self.rupere, self.hulungende = Patient("Taurai Rupere", 101), Patient("Hulungende", 102)
        self.doctor, self.nurse = Doctor("Tawanda Jecheche", 201, 1), Nurse("Kudakwashe Chikumbu", 202, 1)
        for p in (self.rupere, self.hulungende):
            quiet(self.clinic.register_patient, p)
        for s in (self.doctor, self.nurse):
            quiet(self.clinic.register_staff, s)

    def log_text(self):
        with open(self.log_path, encoding="utf-8") as f:
            return f.read()

    def book(self, appt_id, patient, staff, hour):
        return quiet(self.clinic.book_appointment, appt_id, patient, staff, hour)[0]


class PersonTests(unittest.TestCase):
    def test_rejects_bad_names(self):
        for bad in ("", "   ", None, 5):
            with self.subTest(name=bad), self.assertRaises(ValueError):
                Patient(bad, 1)

    def test_rejects_bad_ids(self):
        for bad in (0, -3):
            with self.subTest(id=bad), self.assertRaises(ValueError):
                Patient("Hulungende", bad)
        for bad in (True, "7", 2.5, None):
            with self.subTest(id=bad), self.assertRaises(TypeError):
                Patient("Hulungende", bad)

    def test_name_is_stripped_and_read_only(self):
        p = Patient("  Hulungende ", 1)
        self.assertEqual(p.name, "Hulungende")
        with self.assertRaises(AttributeError):
            p.name = "Bob"
        with self.assertRaises(AttributeError):
            p.id = 9

    def test_person_and_staff_are_abstract(self):
        with self.assertRaises(TypeError):
            Person("Hulungende", 1)
        with self.assertRaises(TypeError):
            Staff("Hulungende", 1)


class FeeTests(unittest.TestCase):
    def test_formulas(self):
        self.assertEqual([Doctor("Tawanda Jecheche", 1, p).fee() for p in (1, 4, 5, 6)], [45, 60, 40, 45])
        self.assertEqual([Nurse("Kudakwashe Chikumbu", 1, p).fee() for p in (1, 2, 3)], [11, 12, 10])
        self.assertEqual(Pharmacist("VaChikumbu", 1).fee(), 5)

    def test_bad_p(self):
        for bad in (0, -1, True, 2.5, None):
            with self.subTest(p=bad), self.assertRaises((TypeError, ValueError)):
                Doctor("Tawanda Jecheche", 1, bad)


class PolymorphismTests(ClinicTestCase):
    def test_new_staff_type_needs_no_clinic_change(self):
        class Dentist(Staff): 
            def role(self):
                return "Dentist"

            def fee(self):
                return 25

        quiet(self.clinic.register_staff, Dentist("VaChikumbu", 250))
        _, out = quiet(self.clinic.show_staff_fees)
        self.assertIn("Dentist 25", out)
        self.assertIn("Doctor 45", out)
        self.assertIn("Nurse 11", out)


class AppointmentTests(unittest.TestCase):
    def make(self, start=10):
        return Appointment(1, Patient("Taurai Rupere", 1), Doctor("Tawanda Jecheche", 2, 1), start)

    def test_legal_transitions(self):
        a = self.make()
        a.confirm()
        self.assertIs(a.status, S.CONFIRMED)
        a.cancel(0, "x")
        self.assertIs(a.status, S.CANCELLED)
        self.assertEqual(a.cancel_reason, "x")

    def test_illegal_transitions(self):
        a = self.make()
        a.confirm()
        with self.assertRaises(IllegalTransition):
            a.confirm() 
        a.cancel(0)
        for action in (a.confirm, lambda: a.cancel(0)): 
            with self.assertRaises(IllegalTransition):
                action()

    def test_confirmed_needs_two_hours_notice(self):
        a = self.make(10)
        a.confirm()
        with self.assertRaisesRegex(IllegalTransition, "too late"):
            a.cancel(9)
        a.cancel(8)  # exactly 2 hours: allowed

    def test_pending_can_be_cancelled_late_but_not_after_start(self):
        self.make(10).cancel(9)
        for now in (10, 11):
            with self.subTest(now=now), self.assertRaisesRegex(IllegalTransition, "started"):
                self.make(10).cancel(now)

    def test_started_confirmed_cannot_be_cancelled(self):
        a = self.make(10)
        a.confirm()
        with self.assertRaises(IllegalTransition):
            a.cancel(10)

    def test_start_hour_bounds(self):
        for bad in (-1, 168):
            with self.assertRaises(ValueError):
                self.make(bad)
        self.make(0)
        self.make(167)


class ClockTests(unittest.TestCase):
    def test_validation_and_monotonic(self):
        for bad in (-1, 169, 1.5, True, "3"):
            with self.subTest(hour=bad), self.assertRaises(ValueError):
                Clock(bad)
        c = Clock(5)
        c.advance(3)
        self.assertEqual(c.now(), 8)
        with self.assertRaises(ValueError):
            c.set_time(2)


class BookingRuleTests(ClinicTestCase):
    def test_happy_path(self):
        a = self.book(301, self.rupere, self.doctor, 10)
        self.assertIs(a.status, S.PENDING)
        self.assertEqual(len(self.clinic.appointments), 1)

    def test_staff_double_booking_rejected(self):
        self.book(301, self.rupere, self.doctor, 10)
        with self.assertRaises(BookingError):
            self.book(302, self.hulungende, self.doctor, 10)

    def test_patient_double_booking_rejected(self):
        self.book(301, self.rupere, self.doctor, 10)
        with self.assertRaises(BookingError):
            self.book(302, self.rupere, self.nurse, 10)

    def test_cancelled_slot_can_be_rebooked(self):
        self.book(301, self.rupere, self.doctor, 10)
        quiet(self.clinic.cancel_appointment, 301)
        self.book(302, self.hulungende, self.doctor, 10)

    def test_ids_unique_across_clinic(self):
        with self.assertRaises(BookingError):
            quiet(self.clinic.register_staff, Nurse("Kudakwashe Chikumbu", 101, 1)) 
        with self.assertRaises(BookingError):
            self.book(101, self.rupere, self.doctor, 10)  
        self.book(301, self.rupere, self.doctor, 10)
        with self.assertRaises(BookingError):
            self.book(301, self.hulungende, self.nurse, 11)

    def test_unregistered_people_rejected(self):
        with self.assertRaises(BookingError):
            self.book(1, Patient("Unregistered Person", 999), self.doctor, 10)
        with self.assertRaises(BookingError):
            self.book(1, self.rupere, Doctor("Unregistered Person", 998, 1), 10)

    def test_cannot_book_in_past_or_now(self):
        self.clock.set_time(10)
        for hour in (3, 10):
            with self.subTest(hour=hour), self.assertRaises(BookingError):
                self.book(1, self.rupere, self.doctor, hour)

    def test_failed_booking_leaves_no_trace(self):
        with self.assertRaises(ValueError):
            self.book(1, self.rupere, self.doctor, 500)
        self.assertEqual(self.clinic.appointments, ())
        self.book(1, self.rupere, self.doctor, 10)  


class EncapsulationTests(ClinicTestCase):
    def test_views_are_immutable_copies(self):
        self.book(301, self.rupere, self.doctor, 10)
        for view in (self.clinic.appointments, self.clinic.patients, self.clinic.staff):
            self.assertIsInstance(view, tuple)
        self.assertEqual(len(self.clinic.appointments), 1)
        self.assertFalse(hasattr(self.clinic.appointments, "append"))

    def test_cannot_assign_internals(self):
        a = self.book(301, self.rupere, self.doctor, 10)
        for attr in ("status", "start_hour", "id"):
            with self.assertRaises(AttributeError):
                setattr(a, attr, 1)


class LoggingTests(ClinicTestCase):
    def test_opened_and_closed_exactly_once_per_action(self):
        _, out = quiet(self.clinic.book_appointment, 301, self.rupere, self.doctor, 10)
        self.assertEqual(out.count("[log] opened"), 1)
        self.assertEqual(out.count("[log] closed"), 1)

    def test_failure_is_logged_and_log_still_closed(self):
        self.book(3, self.rupere, self.doctor, 10)
        quiet(self.clinic.confirm_appointment, 3)
        self.clock.set_time(9)
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer), self.assertRaises(IllegalTransition):
            self.clinic.cancel_appointment(3)
        self.assertIn("[log] opened", buffer.getvalue())
        self.assertIn("[log] closed", buffer.getvalue())
        self.assertIn("FAILED cancel #3: too late", self.log_text())

    def test_success_is_logged(self):
        self.book(301, self.rupere, self.doctor, 10)
        self.assertIn("Booked #301", self.log_text())

    def test_unopenable_log_refuses_action_and_changes_nothing(self):
        broken = Clinic(self.clock, os.path.dirname(self.log_path))  # a directory, not a file
        with self.assertRaises(LogUnavailable):
            quiet(broken.register_patient, Patient("Unregistered Person", 7))
        self.assertEqual(broken.patients, ())

    def test_missing_appointment_is_logged(self):
        with self.assertRaises(ClinicError):
            quiet(self.clinic.cancel_appointment, 77)
        self.assertIn("FAILED cancel #77", self.log_text())


class EmergencyTwistTests(ClinicTestCase):
    def test_emergency_bumps_pending(self):
        old = self.book(301, self.rupere, self.doctor, 10)
        quiet(self.clinic.flag_emergency, 102)
        new = self.book(302, self.hulungende, self.doctor, 10)
        self.assertIs(old.status, S.CANCELLED)
        self.assertEqual(old.cancel_reason, "bumped")
        self.assertIs(new.status, S.PENDING)
        self.assertIn("Bumped #301", self.log_text())

    def test_emergency_cannot_bump_confirmed(self):
        old = self.book(301, self.rupere, self.doctor, 10)
        quiet(self.clinic.confirm_appointment, 301)
        quiet(self.clinic.flag_emergency, 102)
        with self.assertRaisesRegex(BookingError, "CONFIRMED"):
            self.book(302, self.hulungende, self.doctor, 10)
        self.assertIs(old.status, S.CONFIRMED)

    def test_non_emergency_cannot_bump(self):
        old = self.book(301, self.rupere, self.doctor, 10)
        with self.assertRaises(BookingError):
            self.book(302, self.hulungende, self.doctor, 10)
        self.assertIs(old.status, S.PENDING)

    def test_failed_emergency_booking_bumps_nobody(self):
        old = self.book(301, self.rupere, self.doctor, 10)
        self.book(302, self.hulungende, self.nurse, 10)
        quiet(self.clinic.flag_emergency, 102)
        with self.assertRaises(BookingError): 
            self.book(303, self.hulungende, self.doctor, 10)
        self.assertIs(old.status, S.PENDING)


class MedicalLecturerTests(unittest.TestCase):
    def test_one_person_constructor_call(self):
        before = Person.constructed_count()
        MedicalLecturer("Tawanda Jecheche", 1, 2, "Anatomy")
        self.assertEqual(Person.constructed_count() - before, 1)

    def test_role_fee_and_types(self):
        m = MedicalLecturer("Tawanda Jecheche", 1, 2, "Anatomy")
        self.assertEqual(m.role(), "Doctor and Lecturer")
        self.assertEqual(m.fee(), Doctor("Tawanda Jecheche", 2, 2).fee())
        self.assertEqual(m.module, "Anatomy")
        self.assertIsInstance(m, Doctor)
        self.assertIsInstance(m, Lecturer)

    def test_mro_has_person_once(self):
        self.assertEqual(MedicalLecturer.__mro__.count(Person), 1)

    def test_validation_still_applies(self):
        with self.assertRaises(ValueError):
            MedicalLecturer("", 1, 2, "Anatomy")
        with self.assertRaises(ValueError):
            MedicalLecturer("Tawanda Jecheche", 1, 2, " ")


if __name__ == "__main__":
    unittest.main()
