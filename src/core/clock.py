
class Clock:
    """Controls project time without using the computer's clock."""

    def __init__(self, current_hour=0):
        self.__validate_hour(current_hour)
        self.__current_hour = current_hour

    @staticmethod
    def __validate_hour(current_hour):
        if (
            isinstance(current_hour, bool)
            or not isinstance(current_hour, int)
            or not 0 <= current_hour <= 168
        ):
            raise ValueError("Time must be a whole number between 0 and 168.")

    def now(self):
        return self.__current_hour

    def set_time(self, current_hour):
        self.__validate_hour(current_hour)
        self.__current_hour = current_hour
