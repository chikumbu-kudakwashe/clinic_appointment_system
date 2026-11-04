from src.core.clinic import Clinic
from src.core.clock import Clock
from src.errors import ClinicError
from src.models.doctor import Doctor
from src.models.medical_lecturer import MedicalLecturer
from src.models.nurse import Nurse
from src.models.patient import Patient
from src.models.person import Person
from src.models.pharmacist import Pharmacist

P = 9 # Apa sir for 9 we were not sure saka we used 9 so that P mod 4 would be equal to 1


def step(title):
    print(f"\n--- {title} ---")


def main():
    clock = Clock(0)
    clinic = Clinic(clock)
    rupere = Patient("Taurai Rupere", 101)
    hulungende = Patient("Hulungende", 102)
    doctor = Doctor("Tawanda Jecheche", 201, P)
    nurse = Nurse("Kudakwashe Chikumbu", 202, P)
    pharm = Pharmacist("VaChikumbu", 203)
    for p in (rupere, hulungende):
        clinic.register_patient(p)
    for s in (doctor, nurse, pharm):
        clinic.register_staff(s)

    step("FEES (one polymorphic loop)")
    clinic.show_staff_fees()

    step("BOOK + CONFIRM")
    clinic.book_appointment(301, rupere, doctor, 10)
    clinic.confirm_appointment(301)

    step("CLASH REJECTED (staff busy)")
    try:
        clinic.book_appointment(302, hulungende, doctor, 10)
    except ClinicError as e:
        print("Rejected:", e)

    step("EMERGENCY BUMPS A PENDING APPOINTMENT")
    clinic.book_appointment(303, rupere, nurse, 12)
    clinic.flag_emergency(102)
    clinic.book_appointment(304, hulungende, nurse, 12)
    print("303:", clinic.appointments[1].status.value, "| 304:", clinic.appointments[2].status.value)

    step("MEDICAL LECTURER")
    before = Person.constructed_count()
    ml = MedicalLecturer("Prof Tawanda Jecheche", 204, P, "Anatomy")
    print(ml.role(), ml.fee(), "| Person ctor ran", Person.constructed_count() - before, "time(s)")

    step("DELIBERATE FAILURE: cancel CONFIRMED #301 one hour before start")
    clock.set_time(9)
    try:
        clinic.cancel_appointment(301, "changed mind")
    except ClinicError as e:
        print("Rejected:", e)


if __name__ == "__main__":
    main()
