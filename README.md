# Royal Care Clinic - Healthcare Clinic Management System

ICS220 Assignment 2
Abdulla Alhammadi (202324776) and Mohamed Salem (202115227)

A Python program for an outpatient clinic: clinic and department information,
patient accounts, doctors and staff, appointment booking, medical records (EMR),
prescriptions, lab tests, invoices with insurance, and payments.

## Files

| File | Classes |
|------|---------|
| `person.py` | Person |
| `staff.py` | Staff, Doctor |
| `patient.py` | Patient, Insurance |
| `clinic.py` | Clinic, Department |
| `appointment.py` | Appointment |
| `medical_record.py` | MedicalRecord, Prescription, LabOrder |
| `billing.py` | Invoice, Payment, CardPayment, MobileWalletPayment, InsuranceClaim |
| `sample_data.py` | Creates the clinic, staff and doctor schedules |
| `main.py` | Runs the two example scenarios |
| `test_clinic.py` | Test cases (35 tests) |
| `uml/` | UML class diagram |

## How to run

```
python main.py
python -m unittest -v test_clinic
```

Needs Python 3.8 or newer. No extra packages.
