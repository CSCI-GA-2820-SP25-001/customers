######################################################################
# Copyright 2016, 2024 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

"""
Test cases for Customer Model
"""

# pylint: disable=duplicate-code
import os
import logging
from unittest import TestCase
from wsgi import app
from service.models import Customer, DataValidationError, db
from .factories import CustomerFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)


######################################################################
#  C U S T O M E R   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestCustomer(TestCase):
    """Test Cases for Customer Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        with app.app_context():
            db.drop_all()  # clean state before starting tests
            db.create_all()  # explicitly create schema for tests

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        self.app_context = app.app_context()
        self.app_context.push()

        db.session.query(Customer).delete()
        db.session.commit()

    def tearDown(self):
        """Runs after each test"""
        db.session.remove()
        self.app_context.pop()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_customer_success(self):
        """It should create a customer with a valid email"""
        customer = CustomerFactory()
        customer.create()
        self.assertIsNotNone(customer.id)

        found_customer = Customer.find(customer.id)
        self.assertIsNotNone(found_customer)
        self.assertEqual(found_customer.email, customer.email)
        self.assertEqual(found_customer.first_name, customer.first_name)
        self.assertEqual(found_customer.last_name, customer.last_name)
        self.assertEqual(found_customer.address, customer.address)
        self.assertEqual(found_customer.password, customer.password)

    def test_create_customer_invalid_email_format(self):
        """It should raise DataValidationError for invalid email format"""
        customer = CustomerFactory(email="invalid-email-format")
        with self.assertRaises(DataValidationError) as context:
            customer.create()
        self.assertIn("Invalid email format", str(context.exception))

    def test_create_customer_duplicate_email(self):
        """It should raise DataValidationError for duplicate email"""
        existing_customer = CustomerFactory()
        existing_customer.create()

        duplicate_customer = CustomerFactory(email=existing_customer.email)
        with self.assertRaises(DataValidationError) as context:
            duplicate_customer.create()
        self.assertIn("already exists", str(context.exception))

    def test_create_customer_missing_email(self):
        """It should raise DataValidationError when email is missing"""
        data = CustomerFactory().__dict__
        data.pop("email")  # explicitly remove email to test missing field handling

        customer = Customer()
        with self.assertRaises(DataValidationError) as context:
            customer.deserialize(data)
        self.assertIn("missing email", str(context.exception).lower())

    def test_serialize_customer(self):
        """It should serialize a customer object into a dictionary"""
        customer = CustomerFactory()
        customer_dict = customer.serialize()

        self.assertEqual(customer_dict["email"], customer.email)
        self.assertEqual(customer_dict["first_name"], customer.first_name)

    def deserialize(self, data):
        """
        Deserializes a Customer from a dictionary
        """
        try:
            self.first_name = data["first_name"]
            self.last_name = data["last_name"]
            self.email = data["email"]
            self.password = data["password"]
            self.address = data["address"]

            if not self._validate_email_format(self.email):
                raise DataValidationError(f"Invalid email format: '{self.email}'")

        except KeyError as error:
            raise DataValidationError(
                f"Missing required field: {error.args[0]}"
            ) from error
        except TypeError as error:
            raise DataValidationError("Invalid input data") from error

        return self

    def test_customer_id_autogenerated(self):
        """It should auto-generate a Customer ID upon creation"""
        customer = CustomerFactory()
        customer.create()

        self.assertIsNotNone(customer.id)
        self.assertIsInstance(customer.id, int)

    def test_customer_creation_date_autoset(self):
        """It should automatically set creation date on customer creation"""
        customer = CustomerFactory()
        customer.create()

        found_customer = Customer.find(customer.id)
        self.assertIsNotNone(found_customer.creation_date)

    def test_create_customer_missing_first_name(self):
        """It should raise DataValidationError if first name is missing"""
        data = CustomerFactory().serialize()
        data.pop("first_name")

        customer = Customer()
        with self.assertRaises(DataValidationError) as context:
            customer.deserialize(data)
        self.assertIn("missing first_name", str(context.exception).lower())

    def test_create_customer_missing_last_name(self):
        """It should raise DataValidationError if last name is missing"""
        data = CustomerFactory().serialize()
        data.pop("last_name")

        customer = Customer()
        with self.assertRaises(DataValidationError) as context:
            customer.deserialize(data)
        self.assertIn("missing last_name", str(context.exception).lower())

    def test_create_customer_missing_password(self):
        """It should raise DataValidationError if password is missing"""
        data = CustomerFactory().serialize()
        data.pop("password")

        customer = Customer()
        with self.assertRaises(DataValidationError) as context:
            customer.deserialize(data)
        self.assertIn("missing password", str(context.exception).lower())

    def test_create_customer_missing_address(self):
        """It should raise DataValidationError if address is missing"""
        data = CustomerFactory().serialize()
        data.pop("address")

        customer = Customer()
        with self.assertRaises(DataValidationError) as context:
            customer.deserialize(data)
        self.assertIn("missing address", str(context.exception).lower())
