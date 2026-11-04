class ClinicError(Exception):
    """Base class for every rule violation raised by the clinic domain."""


class IllegalTransition(ClinicError):
    """An appointment status change that the rules forbid."""


class BookingError(ClinicError):
    """A booking or registration that breaks a rule."""


class LogUnavailable(ClinicError):
    """The appointment log could not be opened, so the action was refused."""
