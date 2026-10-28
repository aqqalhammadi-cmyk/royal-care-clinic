"""
clinic.py
Clinic and Department classes.

Clinic *-- Department   (composition: departments are created by the clinic
                         and cannot exist without it)
Department o-- Staff    (aggregation: staff exist on their own and can move
                         to another department)
Clinic o-- Patient      (aggregation: the clinic keeps a list of registered patients)
"""

from patient import Patient
from staff import Doctor
from billing import Invoice


class Department:
    """A department of the clinic, e.g. Cardiology."""

    def __init__(self, name, operating_hours):
        self.__name = name
        self.__operating_hours = operating_hours
        self.__staff = []                  # aggregation

    def get_name(self):
        return self.__name

    def get_operating_hours(self):
        return self.__operating_hours

    def set_operating_hours(self, hours):
        self.__operating_hours = hours

    def get_staff(self):
        return self.__staff

    def add_staff(self, staff):
        """Add a staff member. If they were in another department, move them."""
        old_department = staff.get_department()
        if old_department is not None:
            old_department.remove_staff(staff)
        self.__staff.append(staff)
        staff.set_department(self)

    def remove_staff(self, staff):
        self.__staff.remove(staff)
        staff.set_department(None)

    def __str__(self):
        return f"{self.__name} ({self.__operating_hours}) - {len(self.__staff)} staff"


class Clinic:
    """The clinic: its information, departments, patients and invoices."""

    def __init__(self, name, address, phone, email, website):
        self.__name = name
        self.__address = address
        self.__phone = phone
        self.__email = email
        self.__website = website
        self.__departments = []     # composition
        self.__patients = []        # aggregation
        self.__invoices = []

    # ----- clinic information -----
    def get_name(self):
        return self.__name

    def get_address(self):
        return self.__address

    def set_address(self, address):
        self.__address = address

    def get_phone(self):
        return self.__phone

    def set_phone(self, phone):
        self.__phone = phone

    def get_email(self):
        return self.__email

    def set_email(self, email):
        self.__email = email

    def get_website(self):
        return self.__website

    def set_website(self, website):
        self.__website = website

    # ----- departments (composition) -----
    def add_department(self, name, operating_hours):
        """The clinic creates the department."""
        department = Department(name, operating_hours)
        self.__departments.append(department)
        return department

    def remove_department(self, name):
        """Close a department. Its staff are kept but have no department."""
        department = self.get_department(name)
        for staff in list(department.get_staff()):
            department.remove_staff(staff)
        self.__departments.remove(department)

    def get_department(self, name):
        for department in self.__departments:
            if department.get_name() == name:
                return department
        raise ValueError(f"No department called {name}.")

    def get_departments(self):
        return self.__departments

    # ----- staff and doctors -----
    def get_all_staff(self):
        staff_list = []
        for department in self.__departments:
            staff_list.extend(department.get_staff())
        return staff_list

    def get_doctors(self):
        return [s for s in self.get_all_staff() if isinstance(s, Doctor)]

    # ----- patients -----
    def register_patient(self, username, password, name, date_of_birth, phone, email,
                         address, emergency_contact, insurance=None, allergies="None",
                         medical_history="None"):
        """Create a patient account. Usernames must be unique."""
        for patient in self.__patients:
            if patient.get_username() == username:
                raise ValueError("This username is already taken.")
        patient_id = f"P{len(self.__patients) + 1:03d}"
        patient = Patient(patient_id, username, password, name, date_of_birth, phone,
                          email, address, emergency_contact, insurance, allergies,
                          medical_history)
        self.__patients.append(patient)
        return patient

    def login(self, username, password):
        for patient in self.__patients:
            if patient.get_username() == username and patient.check_password(password):
                return patient
        raise PermissionError("Wrong username or password.")

    def get_patients(self):
        return self.__patients

    # ----- appointment search -----
    def search_slots(self, date=None, doctor_name=None, speciality=None):
        """Find available slots by date, doctor name and/or speciality."""
        results = []
        for doctor in self.get_doctors():
            if doctor_name and doctor_name.lower() not in doctor.get_name().lower():
                continue
            if speciality and doctor.get_speciality() != speciality:
                continue
            results.extend(doctor.get_available_slots(date))
        return results

    # ----- billing -----
    def create_invoice(self, record):
        invoice = Invoice(f"INV-{len(self.__invoices) + 1:03d}", record)
        self.__invoices.append(invoice)
        record.get_patient().add_invoice(invoice)
        return invoice

    def get_invoices(self):
        return self.__invoices

    def __str__(self):
        lines = [f"{self.__name}",
                 f"  Address : {self.__address}",
                 f"  Phone   : {self.__phone}",
                 f"  Email   : {self.__email}",
                 f"  Website : {self.__website}",
                 "  Departments:"]
        for department in self.__departments:
            lines.append(f"    - {department}")
        return "\n".join(lines)
