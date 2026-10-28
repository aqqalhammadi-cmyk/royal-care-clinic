"""
medical_record.py
Electronic Medical Record (EMR) for one visit, with its prescriptions
and lab orders.

MedicalRecord *-- Prescription  (composition)
MedicalRecord *-- LabOrder      (composition)
Prescriptions and lab orders are created by the medical record and
cannot exist without it.
"""


class Prescription:
    """A medicine prescribed during a visit."""

    CREATED = "CREATED"
    SENT_TO_PHARMACY = "SENT TO PHARMACY"

    def __init__(self, drug_name, dosage, directions, price):
        self.__drug_name = drug_name
        self.__dosage = dosage
        self.__directions = directions
        self.__price = price
        self.__status = Prescription.CREATED

    def get_drug_name(self):
        return self.__drug_name

    def get_dosage(self):
        return self.__dosage

    def get_directions(self):
        return self.__directions

    def get_price(self):
        return self.__price

    def get_status(self):
        return self.__status

    def send_to_pharmacy(self):
        """Send the prescription to the pharmacy."""
        self.__status = Prescription.SENT_TO_PHARMACY

    def __str__(self):
        return (f"{self.__drug_name} {self.__dosage} - {self.__directions} "
                f"[{self.__status}]")


class LabOrder:
    """A lab test ordered by the doctor. Status: ORDERED -> COMPLETED."""

    ORDERED = "ORDERED"
    COMPLETED = "COMPLETED"

    def __init__(self, test_name, price):
        self.__test_name = test_name
        self.__price = price
        self.__status = LabOrder.ORDERED
        self.__result = None     # filled in when the lab finishes

    def get_test_name(self):
        return self.__test_name

    def get_price(self):
        return self.__price

    def get_status(self):
        return self.__status

    def get_result(self):
        return self.__result

    def add_result(self, result):
        """Store the result. The order becomes COMPLETED."""
        if self.__status == LabOrder.COMPLETED:
            raise ValueError("This lab order already has a result.")
        self.__result = result
        self.__status = LabOrder.COMPLETED

    def __str__(self):
        result = self.__result if self.__result else "waiting"
        return f"{self.__test_name} [{self.__status}] Result: {result}"


class MedicalRecord:
    """The EMR of one visit: notes, diagnosis, vitals, prescriptions,
    lab orders and attachments."""

    def __init__(self, record_id, patient, doctor, appointment, diagnosis, notes, vitals):
        self.__record_id = record_id
        self.__patient = patient
        self.__doctor = doctor
        self.__appointment = appointment
        self.__diagnosis = diagnosis
        self.__notes = notes
        self.__vitals = vitals            # dictionary, e.g. {"BP": "120/80"}
        self.__prescriptions = []         # composition
        self.__lab_orders = []            # composition
        self.__attachments = []           # file names of scanned documents

    # ----- getters -----
    def get_record_id(self):
        return self.__record_id

    def get_patient(self):
        return self.__patient

    def get_doctor(self):
        return self.__doctor

    def get_appointment(self):
        return self.__appointment

    def get_diagnosis(self):
        return self.__diagnosis

    def get_notes(self):
        return self.__notes

    def get_vitals(self):
        return self.__vitals

    def get_prescriptions(self):
        return self.__prescriptions

    def get_lab_orders(self):
        return self.__lab_orders

    def get_attachments(self):
        return self.__attachments

    # ----- adding parts (composition: the record creates them) -----
    def add_prescription(self, drug_name, dosage, directions, price):
        prescription = Prescription(drug_name, dosage, directions, price)
        self.__prescriptions.append(prescription)
        return prescription

    def add_lab_order(self, test_name, price):
        lab_order = LabOrder(test_name, price)
        self.__lab_orders.append(lab_order)
        return lab_order

    def add_attachment(self, file_name):
        self.__attachments.append(file_name)

    # ----- access control -----
    def get_summary(self, viewer):
        """Return the visit summary. Only the patient or clinic staff may see it."""
        if viewer is not self.__patient and not viewer.can_view_records():
            raise PermissionError(f"{viewer.get_name()} cannot view this record.")

        lines = [f"Visit Summary - {self.__record_id}",
                 f"Patient   : {self.__patient.get_name()}",
                 f"Doctor    : {self.__doctor.get_name()}",
                 f"Date      : {self.__appointment.get_date()} {self.__appointment.get_time()}",
                 f"Diagnosis : {self.__diagnosis}",
                 f"Notes     : {self.__notes}",
                 f"Vitals    : {self.__vitals}",
                 "Prescriptions:"]
        for p in self.__prescriptions:
            lines.append(f"  - {p}")
        lines.append("Lab orders:")
        for lab in self.__lab_orders:
            lines.append(f"  - {lab}")
        lines.append(f"Attachments: {', '.join(self.__attachments) or 'None'}")
        return "\n".join(lines)
