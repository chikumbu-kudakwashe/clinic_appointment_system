
from src.models.appointment import AppointmentStatus


class CancellationPolicy:
    """Applies the clinic's appointment cancellation rules."""

    def can_cancel(self, appointment, current_hour):

        if isinstance(current_hour, bool) or not isinstance(current_hour, int):
            raise TypeError("Current hour must be an integer.")

        if not 0 <= current_hour <= 168:
            raise ValueError("Current hour must be between 0 and 168.")

        if appointment.status == AppointmentStatus.CANCELLED:
            return False

        if current_hour >= appointment.start_hour:
            return False

        if (
            appointment.status == AppointmentStatus.CONFIRMED
            and appointment.start_hour - current_hour < 2
        ):
            return False

        return True
