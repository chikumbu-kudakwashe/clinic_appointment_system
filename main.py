
from src.models.patient import Patient
from src.models.doctor import Doctor
from src.models.nurse import Nurse
from src.models.pharmacist import Pharmacist
from src.core.clinic import Clinic
from src.core.clock import Clock


def main():
    # Temporary P value; we will confirm it against your assignment.
    P = 1

    # Create the project clock and clinic.
    clock = Clock(0)
    clinic = Clinic(clock)

    # Create a patient.
    patient = Patient("John", 101)

    # Create clinic staff.
    doctor = Doctor("Dr Smith", 201, P)
    nurse = Nurse("Mary", 202, P)
    pharmacist = Pharmacist("Peter", 203)

    # Register the patient and staff.
    clinic.register_patient(patient)
    clinic.register_staff(doctor)
    clinic.register_staff(nurse)
    clinic.register_staff(pharmacist)

    # Display staff consultation fees.
    print("\n--- STAFF FEES ---")
    clinic.show_staff_fees()

    # Book an appointment.
    print("\n--- BOOKING APPOINTMENT ---")
    appointment = clinic.book_appointment(
        301, patient, doctor, 10
    )

    print("Appointment ID:", appointment.id)
    print("Appointment status:", appointment.status.value)

    # Confirm the appointment.
    print("\n--- CONFIRMING APPOINTMENT ---")
    clinic.confirm_appointment(301)
    print("Appointment status:", appointment.status.value)

    # Demonstrate the project clock.
    print("\n--- PROJECT TIME ---")
    print("Current project hour:", clock.now())


if __name__ == "__main__":
    main()
