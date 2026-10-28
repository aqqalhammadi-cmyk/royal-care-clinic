"""
patient.py
Patient and Insurance classes.

Person <|-- Patient     (inheritance)
Patient o-- Insurance   (aggregation: the insurance policy exists on its own,
                         the patient just has one)
"""

from person import Person


class Insurance:
    """A patient's insurance policy.
    The patient pays a fixed co-pay, then the insurance covers a
    percentage of the rest."""

    def __init__(self, provider, policy_number, coverage_percent, copay):
        self.__provider = provider
        self.__policy_number = policy_number
        self.__coverage_percent = coverage_percent   # e.g. 80
        self.__copay = copay                         # e.g. 50 (AED)

    def get_provider(self):
        return self.__provider

    def get_policy_number(self):
        return self.__policy_number

    def get_coverage_percent(self):
        return self.__coverage_percent

    def get_copay(self):
        return self.__copay

    def calculate_share(self, total):
        """Return (insurance pays, patient pays) for a bill total."""
        copay = min(self.__copay, total)
        insurance_pays = round((total - copay) * self.__coverage_percent / 100, 2)
        patient_pays = round(total - insurance_pays, 2)
        return insurance_pays, patient_pays

    def __str__(self):
        return (f"{self.__provider} ({self.__policy_number}) - "
                f"{self.__coverage_percent}% coverage, co-pay AED {self.__copay}")


class Patient(Person):
    """A patient with an account, personal details and medical information."""

    def __init__(self, patient_id, username, password, name, date_of_birth, phone,
                 email, address, emergency_contact, insurance=None, allergies="None",
                 medical_history="None"):
        super().__init__(patient_id, name, phone, email)
        self.__username = username
        self.__password = password
        self.__date_of_birth = date_of_birth
        self.__address = address
        self.__emergency_contact = emergency_contact
        self.__insurance = insurance          # Insurance object or None
        self.__allergies = allergies
        self.__medical_history = medical_history
        self.__appointments = []              # association with Appointment
        self.__records = []                   # visit records (EMR)
        self.__invoices = []

    # ----- account -----
    def get_username(self):
        return self.__username

    def check_password(self, password):
        return self.__password == password

    # ----- getters and setters -----
    def get_date_of_birth(self):
        return self.__date_of_birth

    def get_address(self):
        return self.__address

    def set_address(self, address):
        self.__address = address

    def get_emergency_contact(self):
        return self.__emergency_contact

    def set_emergency_contact(self, contact):
        self.__emergency_contact = contact

    def get_insurance(self):
        return self.__insurance

    def set_insurance(self, insurance):
        self.__insurance = insurance

    def get_allergies(self):
        return self.__allergies

    def set_allergies(self, allergies):
        self.__allergies = allergies

    def get_medical_history(self):
        return self.__medical_history

    def set_medical_history(self, history):
        self.__medical_history = history

    def get_appointments(self):
        return self.__appointments

    def get_records(self):
        return self.__records

    def get_invoices(self):
        return self.__invoices

    def add_record(self, record):
        self.__records.append(record)

    def add_invoice(self, invoice):
        self.__invoices.append(invoice)

    # ----- appointments -----
    def book_appointment(self, appointment):
        appointment.book(self)          # raises an error if the slot is taken
        self.__appointments.append(appointment)

    def cancel_appointment(self, appointment):
        appointment.cancel()
        self.__appointments.remove(appointment)

    def reschedule_appointment(self, old_appointment, new_appointment):
        """Move to a new slot: book the new one first, then cancel the old one."""
        self.book_appointment(new_appointment)
        self.cancel_appointment(old_appointment)

    def get_upcoming_appointments(self):
        return [a for a in self.__appointments if a.get_status() == "BOOKED"]

    # ----- visit summaries -----
    def download_visit_summaries(self, file_name):
        """Save all visit summaries to a text file."""
        with open(file_name, "w") as file:
            file.write(f"Royal Care Clinic - Visit summaries for {self._name}\n\n")
            for record in self.__records:
                file.write(record.get_summary(self) + "\n\n")
        return file_name

    def __str__(self):
        insurance = self.__insurance if self.__insurance else "No insurance"
        return (f"Patient: {self._name} (ID: {self._person_id})\n"
                f"  Date of birth     : {self.__date_of_birth}\n"
                f"  Phone / Email     : {self._phone} / {self._email}\n"
                f"  Address           : {self.__address}\n"
                f"  Emergency contact : {self.__emergency_contact}\n"
                f"  Insurance         : {insurance}\n"
                f"  Allergies         : {self.__allergies}\n"
                f"  Medical history   : {self.__medical_history}")
