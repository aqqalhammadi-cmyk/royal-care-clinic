"""
person.py
Person is the parent class for Patient and Staff.
It stores the details that every person in the clinic has.
"""


class Person:
    """Parent class for everyone in the clinic (patients and staff)."""

    def __init__(self, person_id, name, phone, email):
        # Protected attributes (one underscore) so child classes can use them
        self._person_id = person_id
        self._name = name
        self._phone = phone
        self._email = email

    # ----- getters and setters -----
    def get_person_id(self):
        return self._person_id

    def get_name(self):
        return self._name

    def set_name(self, name):
        self._name = name

    def get_phone(self):
        return self._phone

    def set_phone(self, phone):
        self._phone = phone

    def get_email(self):
        return self._email

    def set_email(self, email):
        self._email = email

    def can_view_records(self):
        """By default a person cannot view other people's medical records.
        The Staff class overrides this method."""
        return False

    def __str__(self):
        return f"{self._name} (ID: {self._person_id})"
