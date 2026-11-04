from src.models.status import AppointmentStatus


class CancellationPolicy:
    """The single home of the cancellation rules (D1)."""

    MIN_NOTICE_FOR_CONFIRMED = 2

    @classmethod
    def violation(cls, status, start_hour, now):
        if status is AppointmentStatus.CANCELLED:
            return "already cancelled"
        if now >= start_hour:
            return "already started"
        if status is AppointmentStatus.CONFIRMED and start_hour - now < cls.MIN_NOTICE_FOR_CONFIRMED:
            return "too late"
        return None
