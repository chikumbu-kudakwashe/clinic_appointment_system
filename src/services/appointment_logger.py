
class AppointmentLogger:
    """Handles logging of clinic activities."""

    def __init__(self, filename="clinic.log"):
        self.__filename = filename

    def log(self, message):
        with open(self.__filename, "a", encoding="utf-8") as file:
            file.write(str(message) + "\n")

    def open_log(self):
        file = open(self.__filename, "a", encoding="utf-8")
        print("[log] opened")
        return file

    def close_log(self, file):
        if not file.closed:
            file.close()
            print("[log] closed")
