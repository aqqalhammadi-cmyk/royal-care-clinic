"""
appointment.py
An Appointment is a 30-minute time slot in a doctor's schedule.
It starts as AVAILABLE, becomes BOOKED when a patient books it,
and COMPLETED when the doctor records the visit.
"""


class Appointment:
    """A time slot with a doctor that a patient can book."""

    # Possible statuses
    AVAILABLE = "AVAILABLE"
    BOOKED = "BOOKED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"

    def __init__(self, appointment_id, doctor, date, time, duration=30):
        self.__appointment_id = appointment_id
        self.__doctor = doctor
        self.__date = date            # e.g. "2026-11-02"
        self.__time = time            # e.g. "09:30"
        self.__duration = duration    # minutes
        self.__patient = None         # no patient until booked
        self.__status = Appointment.AVAILABLE
        self.__record = None          # medical record after the visit

    # ----- getters -----
    def get_appointment_id(self):
        return self.__appointment_id

    def get_doctor(self):
        return self.__doctor

    def get_date(self):
        return self.__date

    def get_time(self):
        return self.__time

    def get_duration(self):
        return self.__duration

    def get_patient(self):
        return self.__patient

    def get_status(self):
        return self.__status

    def get_record(self):
        return self.__record

    def set_record(self, record):
        self.__record = record

    # ----- actions -----
    def is_available(self):
        """A slot can be booked if it is new or was cancelled."""
        return self.__status in (Appointment.AVAILABLE, Appointment.CANCELLED)

    def book(self, patient):
        """Book this slot for a patient."""
        if not self.is_available():
            raise ValueError("This appointment slot is already booked.")
        self.__patient = patient
        self.__status = Appointment.BOOKED

    def cancel(self):
        """Cancel the booking. The slot becomes free for other patients."""
        if self.__status != Appointment.BOOKED:
            raise ValueError("Only a booked appointment can be cancelled.")
        self.__patient = None
        self.__status = Appointment.CANCELLED

    def complete(self):
        """Mark the appointment as completed after the visit."""
        if self.__status != Appointment.BOOKED:
            raise ValueError("Only a booked appointment can be completed.")
        self.__status = Appointment.COMPLETED

    def __str__(self):
        patient = self.__patient.get_name() if self.__patient else "-"
        return (f"{self.__appointment_id} | {self.__date} {self.__time} "
                f"({self.__duration} min) | {self.__doctor.get_name()} | "
                f"Patient: {patient} | {self.__status}")
