"""
billing.py
Invoices and payments.

Invoice o-- Payment                    (aggregation)
Payment <|-- CardPayment               (inheritance)
Payment <|-- MobileWalletPayment       (inheritance)
Payment <|-- InsuranceClaim            (inheritance)
"""


class Payment:
    """Parent class for all payment methods."""

    def __init__(self, amount):
        self._amount = amount

    def get_amount(self):
        return self._amount

    def get_method(self):
        """Each child class returns its own payment method name."""
        return "Payment"

    def is_insurance(self):
        return False

    def __str__(self):
        return f"{self.get_method()}: AED {self._amount:.2f}"


class CardPayment(Payment):
    """Payment by debit or credit card."""

    def __init__(self, amount, card_last_four):
        super().__init__(amount)
        self.__card_last_four = card_last_four   # only the last 4 digits are kept

    def get_method(self):
        return f"Card (**** {self.__card_last_four})"


class MobileWalletPayment(Payment):
    """Payment by mobile wallet, e.g. Apple Pay."""

    def __init__(self, amount, wallet_name):
        super().__init__(amount)
        self.__wallet_name = wallet_name

    def get_method(self):
        return f"Mobile wallet ({self.__wallet_name})"


class InsuranceClaim(Payment):
    """The part of the bill paid by the insurance company."""

    def __init__(self, amount, insurance):
        super().__init__(amount)
        self.__insurance = insurance

    def get_method(self):
        return f"Insurance claim ({self.__insurance.get_provider()})"

    def is_insurance(self):
        return True


class Invoice:
    """The bill for one visit."""

    def __init__(self, invoice_id, record):
        self.__invoice_id = invoice_id
        self.__record = record               # the visit being billed
        self.__items = []                    # list of (description, amount)
        self.__payments = []                 # aggregation of Payment objects

        # Add all charges from the visit
        doctor = record.get_doctor()
        self.add_item(f"Consultation - {doctor.get_name()}", doctor.get_consultation_fee())
        for lab in record.get_lab_orders():
            self.add_item(f"Lab test - {lab.get_test_name()}", lab.get_price())
        for prescription in record.get_prescriptions():
            self.add_item(f"Medication - {prescription.get_drug_name()}",
                          prescription.get_price())

    def get_invoice_id(self):
        return self.__invoice_id

    def get_record(self):
        return self.__record

    def get_items(self):
        return self.__items

    def get_payments(self):
        return self.__payments

    def add_item(self, description, amount):
        """Add a charge, e.g. another service."""
        self.__items.append((description, amount))

    def get_total(self):
        return round(sum(amount for description, amount in self.__items), 2)

    def get_shares(self):
        """Return (insurance pays, patient pays)."""
        insurance = self.__record.get_patient().get_insurance()
        if insurance is None:
            return 0, self.get_total()
        return insurance.calculate_share(self.get_total())

    def get_amount_paid(self):
        return round(sum(p.get_amount() for p in self.__payments), 2)

    def get_balance(self):
        return round(self.get_total() - self.get_amount_paid(), 2)

    def get_status(self):
        if self.get_amount_paid() == 0:
            return "UNPAID"
        if self.get_balance() > 0:
            return "PARTIALLY PAID"
        return "PAID"

    def pay(self, payment):
        """Accept any kind of Payment (polymorphism)."""
        if payment.get_amount() <= 0 or payment.get_amount() > self.get_balance():
            raise ValueError("Invalid payment amount.")
        self.__payments.append(payment)

    def __str__(self):
        insurance_pays, patient_pays = self.get_shares()
        lines = ["=" * 54,
                 f"INVOICE {self.__invoice_id}  -  Royal Care Clinic",
                 f"Patient: {self.__record.get_patient().get_name()}",
                 "-" * 54]
        for description, amount in self.__items:
            lines.append(f"{description:<42}{amount:>12.2f}")
        lines += ["-" * 54,
                  f"{'Total':<42}{self.get_total():>12.2f}",
                  f"{'Insurance pays':<42}{insurance_pays:>12.2f}",
                  f"{'Patient pays':<42}{patient_pays:>12.2f}",
                  "-" * 54]
        for payment in self.__payments:
            lines.append(f"{'Paid by ' + payment.get_method():<42}{payment.get_amount():>12.2f}")
        lines += [f"{'Balance':<42}{self.get_balance():>12.2f}",
                  f"Status: {self.get_status()}",
                  "=" * 54]
        return "\n".join(lines)
