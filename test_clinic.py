"""
test_clinic.py
Test cases for the Royal Care Clinic system (separate file).
Covers cases a-h from the assignment, the other features, and the two
example scenarios.

Run with:  python -m unittest -v test_clinic
"""

import os
import unittest

from billing import CardPayment, MobileWalletPayment, InsuranceClaim
from patient import Insurance
from sample_data import create_clinic, NEXT_MONDAY, NEXT_TUESDAY


class ClinicTest(unittest.TestCase):
    """setUp runs before every test, so each test starts with a fresh clinic."""

    def setUp(self):
        self.clinic, self.staff = create_clinic()
        self.dr_brown = self.staff["brown"]
        self.dr_haddad = self.staff["haddad"]
        self.insurance = Insurance("Daman", "DMN-7788", 80, 50)
        self.aliyah = self.clinic.register_patient(
            "aliyah", "pass123", "Aliyah", "2001-03-14", "055 123 4567",
            "aliyah@email.com", "Al Reem Island", "Imran 055 765 4321",
            self.insurance, "Penicillin", "Mild asthma")

    def book_and_visit(self):
        """Helper: Aliyah books Dr. Brown and the visit is recorded."""
        slot = self.dr_brown.get_available_slots(NEXT_MONDAY)[0]
        self.aliyah.book_appointment(slot)
        record = self.dr_brown.record_visit(slot, "Tonsillitis", "Sore throat",
                                            {"Temp": "38.4 C", "BP": "118/76"})
        return slot, record


# ---------------- Clinic information and staff ----------------
class TestClinicInformation(ClinicTest):

    def test_retrieve_clinic_info(self):
        self.assertEqual(self.clinic.get_name(), "Royal Care Clinic")
        self.assertEqual(self.clinic.get_email(), "info@royalcare.ae")
        self.assertEqual(len(self.clinic.get_departments()), 6)

    def test_update_clinic_info(self):
        self.clinic.set_phone("+971 2 555 0111")
        self.clinic.set_website("www.royalcareclinic.ae")
        self.assertEqual(self.clinic.get_phone(), "+971 2 555 0111")
        self.assertEqual(self.clinic.get_website(), "www.royalcareclinic.ae")

    def test_add_and_remove_department(self):
        self.clinic.add_department("Dermatology", "Mon-Thu 10:00-18:00")
        self.assertEqual(self.clinic.get_department("Dermatology").get_operating_hours(),
                         "Mon-Thu 10:00-18:00")
        self.clinic.remove_department("Dermatology")
        with self.assertRaises(ValueError):
            self.clinic.get_department("Dermatology")

    def test_staff_still_exist_when_department_closes(self):
        """Aggregation: removing a department does not delete its staff."""
        dr_khalid = self.staff["khalid"]
        self.clinic.remove_department("Cardiology")
        self.assertIsNone(dr_khalid.get_department())
        self.assertEqual(dr_khalid.get_name(), "Dr. Khalid")

    def test_staff_and_doctors(self):
        self.assertEqual(len(self.clinic.get_all_staff()), 5)
        self.assertEqual(len(self.clinic.get_doctors()), 3)
        self.assertEqual(self.dr_brown.get_role(), "Doctor")       # inherited from Staff
        self.assertEqual(self.dr_brown.get_department().get_name(), "General Practice")

    def test_move_staff_to_other_department(self):
        nurse = self.staff["nurse"]
        self.clinic.get_department("Paediatrics").add_staff(nurse)
        self.assertEqual(nurse.get_department().get_name(), "Paediatrics")
        self.assertNotIn(nurse, self.clinic.get_department("General Practice").get_staff())


# ---------------- a. Patient account creation ----------------
class TestPatientAccount(ClinicTest):

    def test_patient_details_stored(self):
        self.assertEqual(self.aliyah.get_name(), "Aliyah")
        self.assertEqual(self.aliyah.get_date_of_birth(), "2001-03-14")
        self.assertEqual(self.aliyah.get_address(), "Al Reem Island")
        self.assertEqual(self.aliyah.get_insurance().get_provider(), "Daman")
        self.assertEqual(self.aliyah.get_allergies(), "Penicillin")
        self.assertEqual(self.aliyah.get_medical_history(), "Mild asthma")
        self.assertIn(self.aliyah, self.clinic.get_patients())

    def test_login(self):
        self.assertIs(self.clinic.login("aliyah", "pass123"), self.aliyah)
        with self.assertRaises(PermissionError):
            self.clinic.login("aliyah", "wrong")

    def test_username_must_be_unique(self):
        with self.assertRaises(ValueError):
            self.clinic.register_patient("aliyah", "x", "Other", "2000-01-01", "050",
                                         "", "Dubai", "None")

    def test_update_profile(self):
        self.aliyah.set_phone("055 999 0001")
        self.aliyah.set_address("Saadiyat Island")
        self.assertEqual(self.aliyah.get_phone(), "055 999 0001")
        self.assertEqual(self.aliyah.get_address(), "Saadiyat Island")


# ---------------- b. Search for available appointments ----------------
class TestSearchAppointments(ClinicTest):

    def test_search_by_date(self):
        slots = self.clinic.search_slots(date=NEXT_MONDAY)
        self.assertEqual(len(slots), 6)        # Dr. Brown 4 + Dr. Haddad 2

    def test_search_by_doctor(self):
        slots = self.clinic.search_slots(doctor_name="Haddad")
        self.assertEqual(len(slots), 5)

    def test_search_by_speciality(self):
        slots = self.clinic.search_slots(speciality="Cardiologist")
        self.assertEqual(len(slots), 1)
        self.assertEqual(slots[0].get_doctor().get_name(), "Dr. Khalid")

    def test_booked_slot_not_listed(self):
        slot = self.dr_brown.get_available_slots()[0]
        self.aliyah.book_appointment(slot)
        self.assertNotIn(slot, self.clinic.search_slots(date=NEXT_MONDAY))


# ---------------- c. Make an appointment ----------------
class TestMakeAppointment(ClinicTest):

    def test_book_appointment(self):
        slot = self.dr_brown.get_available_slots(NEXT_MONDAY)[0]
        self.aliyah.book_appointment(slot)
        self.assertEqual(slot.get_status(), "BOOKED")
        self.assertIs(slot.get_patient(), self.aliyah)
        self.assertEqual(slot.get_duration(), 30)
        self.assertIn(slot, self.aliyah.get_upcoming_appointments())

    def test_cannot_double_book(self):
        slot = self.dr_brown.get_available_slots()[0]
        self.aliyah.book_appointment(slot)
        omar = self.clinic.register_patient("omar", "x", "Omar", "2019-06-02", "050",
                                            "", "MBZ City", "Mariam")
        with self.assertRaises(ValueError):
            omar.book_appointment(slot)

    def test_reschedule(self):
        old, new = self.dr_brown.get_available_slots()[0:2]
        self.aliyah.book_appointment(old)
        self.aliyah.reschedule_appointment(old, new)
        self.assertEqual(new.get_status(), "BOOKED")
        self.assertTrue(old.is_available())
        self.assertEqual(self.aliyah.get_appointments(), [new])


# ---------------- d. Visit recording and EMR ----------------
class TestVisitRecording(ClinicTest):

    def test_record_linked_to_appointment(self):
        slot, record = self.book_and_visit()
        self.assertIs(slot.get_record(), record)
        self.assertIs(record.get_appointment(), slot)
        self.assertIs(record.get_patient(), self.aliyah)
        self.assertEqual(record.get_diagnosis(), "Tonsillitis")
        self.assertEqual(record.get_vitals()["BP"], "118/76")
        self.assertEqual(slot.get_status(), "COMPLETED")
        self.assertIn(record, self.aliyah.get_records())

    def test_attachment(self):
        slot, record = self.book_and_visit()
        record.add_attachment("xray_report.pdf")
        self.assertIn("xray_report.pdf", record.get_attachments())

    def test_wrong_doctor_cannot_record(self):
        slot = self.dr_brown.get_available_slots()[0]
        self.aliyah.book_appointment(slot)
        with self.assertRaises(PermissionError):
            self.dr_haddad.record_visit(slot, "Flu", "Notes", {})

    def test_access_control(self):
        slot, record = self.book_and_visit()
        self.assertIn("Tonsillitis", record.get_summary(self.aliyah))         # patient
        self.assertIn("Tonsillitis", record.get_summary(self.staff["nurse"]))  # staff
        other = self.clinic.register_patient("other", "x", "Other", "1990-01-01",
                                             "050", "", "Dubai", "None")
        with self.assertRaises(PermissionError):
            record.get_summary(other)

    def test_download_visit_summaries(self):
        self.book_and_visit()
        file_name = self.aliyah.download_visit_summaries("test_summary.txt")
        with open(file_name) as file:
            text = file.read()
        os.remove(file_name)
        self.assertIn("Tonsillitis", text)


# ---------------- e. Prescription generation ----------------
class TestPrescription(ClinicTest):

    def test_prescription_sent_to_pharmacy(self):
        slot, record = self.book_and_visit()
        prescription = self.dr_brown.prescribe(record, "Azithromycin", "500 mg",
                                               "Once a day for 3 days", 36)
        self.assertEqual(prescription.get_status(), "SENT TO PHARMACY")
        self.assertEqual(prescription.get_drug_name(), "Azithromycin")
        self.assertEqual(prescription.get_dosage(), "500 mg")
        self.assertEqual(prescription.get_directions(), "Once a day for 3 days")
        self.assertIn(prescription, record.get_prescriptions())


# ---------------- f. Lab order lifecycle ----------------
class TestLabOrder(ClinicTest):

    def test_lab_order_completed(self):
        slot, record = self.book_and_visit()
        lab = self.dr_brown.order_lab_test(record, "Blood Test", 120)
        self.assertEqual(lab.get_status(), "ORDERED")
        self.assertIsNone(lab.get_result())
        lab.add_result("Normal")
        self.assertEqual(lab.get_status(), "COMPLETED")
        self.assertEqual(lab.get_result(), "Normal")

    def test_result_linked_to_patient_and_visit(self):
        slot, record = self.book_and_visit()
        lab = self.dr_brown.order_lab_test(record, "Blood Test", 120)
        self.assertIn(lab, record.get_lab_orders())
        self.assertIs(record.get_patient(), self.aliyah)

    def test_result_cannot_be_added_twice(self):
        slot, record = self.book_and_visit()
        lab = self.dr_brown.order_lab_test(record, "Blood Test", 120)
        lab.add_result("Normal")
        with self.assertRaises(ValueError):
            lab.add_result("Changed")


# ---------------- g. Invoice generation and payment ----------------
class TestInvoice(ClinicTest):

    def make_invoice(self):
        slot, record = self.book_and_visit()
        self.dr_brown.order_lab_test(record, "Blood Test", 120)
        self.dr_brown.prescribe(record, "Azithromycin", "500 mg", "Daily", 36)
        return self.clinic.create_invoice(record)

    def test_invoice_total(self):
        invoice = self.make_invoice()
        self.assertEqual(invoice.get_total(), 456)        # 300 + 120 + 36
        invoice.add_item("Nebuliser", 44)
        self.assertEqual(invoice.get_total(), 500)

    def test_insurance_and_copay(self):
        invoice = self.make_invoice()
        # co-pay 50, insurance pays 80% of 406 = 324.80, patient pays 50 + 81.20
        self.assertEqual(invoice.get_shares(), (324.80, 131.20))

    def test_insurance_claim_and_card_payment(self):
        invoice = self.make_invoice()
        self.assertEqual(invoice.get_status(), "UNPAID")
        invoice.pay(InsuranceClaim(324.80, self.insurance))
        self.assertEqual(invoice.get_status(), "PARTIALLY PAID")
        invoice.pay(CardPayment(131.20, "4417"))
        self.assertEqual(invoice.get_status(), "PAID")
        self.assertEqual(invoice.get_balance(), 0)

    def test_mobile_wallet_and_overpayment(self):
        invoice = self.make_invoice()
        invoice.pay(MobileWalletPayment(400, "Apple Pay"))
        with self.assertRaises(ValueError):
            invoice.pay(MobileWalletPayment(100, "Apple Pay"))   # only 56 left

    def test_no_insurance(self):
        self.aliyah.set_insurance(None)
        invoice = self.make_invoice()
        self.assertEqual(invoice.get_shares(), (0, 456))


# ---------------- h. Appointment cancellation ----------------
class TestCancellation(ClinicTest):

    def test_cancel_appointment(self):
        slot = self.dr_brown.get_available_slots()[0]
        self.aliyah.book_appointment(slot)
        self.aliyah.cancel_appointment(slot)
        self.assertEqual(slot.get_status(), "CANCELLED")
        self.assertTrue(slot.is_available())                 # free for others
        self.assertEqual(self.aliyah.get_upcoming_appointments(), [])

    def test_cannot_cancel_completed_visit(self):
        slot, record = self.book_and_visit()
        with self.assertRaises(ValueError):
            slot.cancel()


# ---------------- Example scenario 1 ----------------
class TestScenarioAliyah(unittest.TestCase):

    def test_aliyah_visit(self):
        # 1. Create patient Aliyah and doctor Dr. Brown (General Practitioner)
        clinic, staff = create_clinic()
        dr_brown = staff["brown"]
        insurance = Insurance("Daman", "DMN-7788", 80, 50)
        aliyah = clinic.register_patient("aliyah", "pass123", "Aliyah", "2001-03-14",
                                         "055 123 4567", "aliyah@email.com",
                                         "Al Reem Island", "Imran", insurance)
        self.assertEqual(dr_brown.get_speciality(), "General Practitioner")

        # 2. Aliyah books a 30-minute appointment next Monday
        slot = clinic.search_slots(date=NEXT_MONDAY, speciality="General Practitioner")[0]
        aliyah.book_appointment(slot)
        self.assertEqual(slot.get_duration(), 30)

        # 3. Visit: diagnosis, lab tests, prescription
        record = dr_brown.record_visit(slot, "Tonsillitis", "Sore throat",
                                       {"Temp": "38.4 C"})
        blood = dr_brown.order_lab_test(record, "Complete Blood Count", 120)
        strep = dr_brown.order_lab_test(record, "Strep A Test", 90)
        prescription = dr_brown.prescribe(record, "Azithromycin", "500 mg", "Daily", 36)

        # 4. Lab results uploaded, invoice generated, payment completed
        blood.add_result("WBC slightly high")
        strep.add_result("Positive")
        invoice = clinic.create_invoice(record)
        insurance_pays, patient_pays = invoice.get_shares()
        invoice.pay(InsuranceClaim(insurance_pays, insurance))
        invoice.pay(CardPayment(patient_pays, "4417"))

        # 5. Assertions: visit data, prescription and billing are accurate
        self.assertEqual(record.get_diagnosis(), "Tonsillitis")
        self.assertEqual(slot.get_status(), "COMPLETED")
        self.assertEqual(blood.get_status(), "COMPLETED")
        self.assertEqual(prescription.get_status(), "SENT TO PHARMACY")
        self.assertEqual(invoice.get_total(), 546)            # 300 + 120 + 90 + 36
        self.assertEqual(invoice.get_shares(), (396.80, 149.20))
        self.assertEqual(invoice.get_status(), "PAID")


# ---------------- Example scenario 2 ----------------
class TestScenarioOmar(unittest.TestCase):

    def test_omar_visit(self):
        clinic, staff = create_clinic()
        dr_haddad = staff["haddad"]
        omar = clinic.register_patient("omar", "family2026", "Omar", "2019-06-02",
                                       "050 246 8101", "", "MBZ City", "Mariam")

        # Book, reschedule to Tuesday, then book and cancel another slot
        slots = clinic.search_slots(speciality="Paediatrician")
        omar.book_appointment(slots[0])
        omar.reschedule_appointment(slots[0], slots[3])
        omar.book_appointment(slots[4])
        omar.cancel_appointment(slots[4])
        self.assertEqual(omar.get_upcoming_appointments(), [slots[3]])
        self.assertEqual(slots[3].get_date(), NEXT_TUESDAY)

        # Visit with attachment, prescription and lab test
        record = dr_haddad.record_visit(slots[3], "Ear infection", "Left ear pain",
                                        {"Temp": "38.9 C"})
        record.add_attachment("referral.pdf")
        dr_haddad.prescribe(record, "Amoxicillin syrup", "250 mg/5 ml", "Twice a day", 38)
        lab = dr_haddad.order_lab_test(record, "Ear pressure test", 150)
        lab.add_result("Fluid behind eardrum")

        # No insurance: the family pays everything by mobile wallet
        invoice = clinic.create_invoice(record)
        invoice.add_item("Ear examination", 60)
        self.assertEqual(invoice.get_total(), 598)            # 350 + 150 + 38 + 60
        invoice.pay(MobileWalletPayment(598, "Apple Pay"))

        self.assertEqual(lab.get_status(), "COMPLETED")
        self.assertEqual(record.get_attachments(), ["referral.pdf"])
        self.assertEqual(invoice.get_status(), "PAID")


if __name__ == "__main__":
    unittest.main(verbosity=2)
