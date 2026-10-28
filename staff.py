"""
staff.py
Staff and Doctor classes.

Person <|-- Staff <|-- Doctor   (inheritance)
Doctor *-- Appointment          (composition: a doctor creates his own time slots)
"""

from person import Person
from appointment import Appointment
from medical_record import MedicalRecord


class Staff(Person):
    """Any clinic employee: nurse, receptionist, lab technician, doctor..."""

    def __init__(self, staff_id, name, phone, email, role, qualifications, working_hours):
        super().__init__(staff_id, name, phone, email)   # Person's attributes
        self._role = role                    # e.g. "Nurse"
        self._qualifications = qualifications
        self._working_hours = working_hours  # e.g. "Sun-Thu 08:00-16:00"
        self._department = None              # set when added to a department

    def get_role(self):
        return self._role

    def set_role(self, role):
        self._role = role

    def get_qualifications(self):
        return self._qualifications

    def get_working_hours(self):
        return self._working_hours

    def set_working_hours(self, working_hours):
        self._working_hours = working_hours

    def get_department(self):
        return self._department

    def set_department(self, department):
        self._department = department

    def can_view_records(self):
        """Overrides Person: staff members are allowed to view medical records."""
        return True

    def __str__(self):
        department = self._department.get_name() if self._department else "None"
        return f"{self._name} | {self._role} | {department} | {self._working_hours}"


class Doctor(Staff):
    """A doctor is a staff member with a speciality and a schedule."""

    record_counter = 0   # class attribute used to make record IDs

    def __init__(self, staff_id, name, phone, email, speciality, qualifications,
                 working_hours, consultation_fee):
        super().__init__(staff_id, name, phone, email, "Doctor", qualifications, working_hours)
        self.__speciality = speciality            # e.g. "General Practitioner"
        self.__consultation_fee = consultation_fee
        self.__appointments = []                  # composition: doctor's time slots

    def get_speciality(self):
        return self.__speciality

    def get_consultation_fee(self):
        return self.__consultation_fee

    def set_consultation_fee(self, fee):
        self.__consultation_fee = fee

    def get_appointments(self):
        return self.__appointments

    # ----- schedule -----
    def add_slot(self, date, time, duration=30):
        """Create a new available time slot in this doctor's schedule."""
        slot_id = f"{self._person_id}-{len(self.__appointments) + 1}"
        slot = Appointment(slot_id, self, date, time, duration)
        self.__appointments.append(slot)
        return slot

    def get_available_slots(self, date=None):
        """Free slots, optionally only on one date."""
        return [a for a in self.__appointments
                if a.is_available() and (date is None or a.get_date() == date)]

    # ----- clinical work -----
    def record_visit(self, appointment, diagnosis, notes, vitals):
        """Create the medical record for a booked appointment."""
        if appointment.get_doctor() is not self:
            raise PermissionError("This appointment belongs to another doctor.")
        Doctor.record_counter += 1
        record_id = f"EMR-{Doctor.record_counter:03d}"
        patient = appointment.get_patient()
        record = MedicalRecord(record_id, patient, self, appointment, diagnosis, notes, vitals)
        appointment.complete()            # raises an error if not booked
        appointment.set_record(record)
        patient.add_record(record)
        return record

    def prescribe(self, record, drug_name, dosage, directions, price):
        """Write a prescription and send it to the pharmacy."""
        prescription = record.add_prescription(drug_name, dosage, directions, price)
        prescription.send_to_pharmacy()
        return prescription

    def order_lab_test(self, record, test_name, price):
        return record.add_lab_order(test_name, price)

    def __str__(self):
        return super().__str__() + f" | {self.__speciality}"
