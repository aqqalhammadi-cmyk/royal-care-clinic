"""
main.py
Runs the Royal Care Clinic system with two example scenarios.
Run with:  python main.py
"""

from billing import CardPayment, MobileWalletPayment, InsuranceClaim
from patient import Insurance
from sample_data import create_clinic, NEXT_MONDAY


def title(text):
    """Print a section title."""
    print("\n" + "=" * 60)
    print(text)
    print("=" * 60)


def show_clinic(clinic, staff):
    title("CLINIC INFORMATION")
    print(clinic)
    clinic.set_website("www.royalcareclinic.ae")
    print(f"\nWebsite updated to: {clinic.get_website()}")

    print("\nStaff:")
    for person in clinic.get_all_staff():
        print(f"  {person}")


def scenario_aliyah(clinic, staff):
    title("SCENARIO 1: Aliyah visits Dr. Brown")
    dr_brown = staff["brown"]

    # 1. Create patient account
    insurance = Insurance("Daman", "DMN-7788", 80, 50)
    aliyah = clinic.register_patient("aliyah", "pass123", "Aliyah", "2001-03-14",
                                     "055 123 4567", "aliyah@email.com",
                                     "Al Reem Island, Abu Dhabi", "Imran (brother) 055 765 4321",
                                     insurance, "Penicillin", "Mild asthma")
    print("Account created:")
    print(aliyah)

    # 2. Search and book a 30-minute appointment next Monday
    print(f"\nGeneral Practitioner slots on {NEXT_MONDAY}:")
    slots = clinic.search_slots(date=NEXT_MONDAY, speciality="General Practitioner")
    for slot in slots:
        print(f"  {slot}")
    aliyah.book_appointment(slots[1])
    appointment = slots[1]
    print(f"\nBooked: {appointment}")

    # 3. Doctor records the visit, orders lab tests and prescribes
    record = dr_brown.record_visit(appointment, "Tonsillitis",
                                   "Sore throat and fever for 3 days",
                                   {"Temp": "38.4 C", "BP": "118/76", "HR": 96})
    blood_test = dr_brown.order_lab_test(record, "Complete Blood Count", 120)
    strep_test = dr_brown.order_lab_test(record, "Strep A Test", 90)
    prescription = dr_brown.prescribe(record, "Azithromycin", "500 mg",
                                      "Once a day for 3 days", 36)
    dr_brown.prescribe(record, "Paracetamol", "500 mg", "Every 6 hours if needed", 15)
    print(f"\nAppointment status : {appointment.get_status()}")
    print(f"Prescription status: {prescription.get_status()}")
    print(f"Lab test status    : {blood_test.get_status()}")

    # 4. Lab results are uploaded
    blood_test.add_result("WBC slightly high")
    strep_test.add_result("Positive")
    print(f"Lab test status after results: {blood_test.get_status()}")

    print("\n" + record.get_summary(aliyah))

    # 5. Invoice and payment: insurance claim + card
    invoice = clinic.create_invoice(record)
    insurance_pays, patient_pays = invoice.get_shares()
    invoice.pay(InsuranceClaim(insurance_pays, insurance))
    invoice.pay(CardPayment(patient_pays, "4417"))
    print("\n" + str(invoice))

    file_name = aliyah.download_visit_summaries("aliyah_visit_summaries.txt")
    print(f"\nVisit summaries downloaded to {file_name}")


def scenario_omar(clinic, staff):
    title("SCENARIO 2: Omar visits Dr. Haddad")
    dr_haddad = staff["haddad"]

    omar = clinic.register_patient("omar", "family2026", "Omar", "2019-06-02",
                                   "050 246 8101", "saeed.family@email.com",
                                   "MBZ City, Abu Dhabi", "Mariam (mother) 050 246 8101",
                                   allergies="Peanuts")
    print(f"Account created for {omar.get_name()} (no insurance)")

    # Search by doctor name, book, then reschedule
    slots = clinic.search_slots(doctor_name="Haddad")
    print(f"\nFree slots with Dr. Haddad: {len(slots)}")
    first = slots[0]
    omar.book_appointment(first)
    print(f"Booked      : {first}")
    new = slots[3]
    omar.reschedule_appointment(first, new)
    print(f"Rescheduled : {new}")
    print(f"Old slot is free again: {first.is_available()}")

    # Book a second appointment and cancel it
    extra = slots[4]
    omar.book_appointment(extra)
    omar.cancel_appointment(extra)
    print(f"Cancelled   : {extra}")
    print(f"Upcoming appointments for Omar: {len(omar.get_upcoming_appointments())}")

    # Visit with an attachment, prescription and lab test
    record = dr_haddad.record_visit(new, "Ear infection", "Pain in left ear",
                                    {"Temp": "38.9 C", "HR": 118})
    record.add_attachment("school_nurse_referral.pdf")
    dr_haddad.prescribe(record, "Amoxicillin syrup", "250 mg/5 ml", "7.5 ml twice a day", 38)
    hearing = dr_haddad.order_lab_test(record, "Ear pressure test", 150)
    hearing.add_result("Fluid behind left eardrum")
    print("\n" + record.get_summary(staff["nurse"]))

    # Access control: another patient cannot see Omar's record
    aliyah = clinic.login("aliyah", "pass123")
    try:
        record.get_summary(aliyah)
    except PermissionError as error:
        print(f"\nAccess denied: {error}")

    # Invoice with an extra service, paid by mobile wallet
    invoice = clinic.create_invoice(record)
    invoice.add_item("Ear examination", 60)
    invoice.pay(MobileWalletPayment(invoice.get_total(), "Apple Pay"))
    print("\n" + str(invoice))


def main():
    clinic, staff = create_clinic()
    show_clinic(clinic, staff)
    scenario_aliyah(clinic, staff)
    scenario_omar(clinic, staff)
    title("END")


if __name__ == "__main__":
    main()
