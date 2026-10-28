"""
sample_data.py
Creates the Royal Care Clinic with its departments, staff and doctor
schedules. Used by main.py and by the test file.
"""

from clinic import Clinic
from staff import Staff, Doctor

NEXT_MONDAY = "2026-11-02"
NEXT_TUESDAY = "2026-11-03"


def create_clinic():
    """Build the clinic and return it together with the main staff objects."""
    clinic = Clinic("Royal Care Clinic", "Khalifa City, Abu Dhabi",
                    "+971 2 555 0100", "info@royalcare.ae", "www.royalcare.ae")

    # Departments (created by the clinic - composition)
    general = clinic.add_department("General Practice", "Sun-Thu 08:00-20:00")
    paediatrics = clinic.add_department("Paediatrics", "Mon-Fri 09:00-17:00")
    cardiology = clinic.add_department("Cardiology", "Mon-Wed 08:00-15:00")
    laboratory = clinic.add_department("Laboratory", "Daily 07:00-19:00")
    clinic.add_department("Radiology", "Mon-Fri 08:00-16:00")
    clinic.add_department("Pharmacy", "Daily 08:00-22:00")

    # Doctors
    dr_brown = Doctor("D001", "Dr. Brown", "050 111 2233", "brown@royalcare.ae",
                      "General Practitioner", "MBBS", "Mon-Fri 08:00-16:00", 300)
    dr_haddad = Doctor("D002", "Dr. Layla Haddad", "050 222 3344", "haddad@royalcare.ae",
                       "Paediatrician", "MD Paediatrics", "Mon-Thu 09:00-17:00", 350)
    dr_khalid = Doctor("D003", "Dr. Khalid", "050 333 4455", "khalid@royalcare.ae",
                       "Cardiologist", "MD Cardiology", "Mon-Wed 08:00-15:00", 500)

    # Other staff
    nurse = Staff("S001", "Fatima", "050 444 5566", "fatima@royalcare.ae",
                  "Nurse", "BSc Nursing", "Sun-Thu 08:00-16:00")
    lab_tech = Staff("S002", "Rahul", "050 555 6677", "rahul@royalcare.ae",
                     "Lab Technician", "BSc Medical Lab Science", "Sun-Thu 07:00-15:00")

    # Put staff in departments (aggregation)
    general.add_staff(dr_brown)
    general.add_staff(nurse)
    paediatrics.add_staff(dr_haddad)
    cardiology.add_staff(dr_khalid)
    laboratory.add_staff(lab_tech)

    # Doctor schedules: 30-minute slots
    for time in ["09:00", "09:30", "10:00", "10:30"]:
        dr_brown.add_slot(NEXT_MONDAY, time)
    for time in ["10:00", "10:30"]:
        dr_haddad.add_slot(NEXT_MONDAY, time)
    for time in ["09:00", "09:30", "10:00"]:
        dr_haddad.add_slot(NEXT_TUESDAY, time)
    dr_khalid.add_slot(NEXT_TUESDAY, "08:00")

    staff = {"brown": dr_brown, "haddad": dr_haddad, "khalid": dr_khalid,
             "nurse": nurse, "lab_tech": lab_tech}
    return clinic, staff
