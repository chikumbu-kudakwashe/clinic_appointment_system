class Clock:

    MAX_HOUR = 168

    def __init__(self, current_hour=0):
        self.__current_hour = self.__validate(current_hour)

    @classmethod
    def __validate(cls, hour):
        if isinstance(hour, bool) or not isinstance(hour, int) or not 0 <= hour <= cls.MAX_HOUR:
            raise ValueError(f"Time must be a whole number between 0 and {cls.MAX_HOUR}.")
        return hour

    def now(self):
        return self.__current_hour

    def set_time(self, hour):
        hour = self.__validate(hour)
        if hour < self.__current_hour:
            raise ValueError("Time cannot go backwards.")
        self.__current_hour = hour

    def advance(self, hours):
        self.set_time(self.__current_hour + hours)
