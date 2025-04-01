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
import re
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
        """This runs after each test"""
        db.session.remove()

    @staticmethod
    def _validate_email_format(email):
        """Validates email format using regex."""
        email_regex = r"(^[\w\.\+-]+@[\w-]+\.[a-zA-Z]{2,}$)"
        return re.match(email_regex, email) is not None

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
        data = CustomerFactory().serialize()
        data.pop("email")  # explicitly remove email to test missing field handling

        with self.assertRaises(DataValidationError) as context:
            Customer(**data)
        self.assertIn("missing email", str(context.exception).lower())

    def test_serialize_customer(self):
        """It should serialize a customer object into a dictionary"""
        customer = CustomerFactory()
        customer_dict = customer.serialize()

        self.assertEqual(customer_dict["email"], customer.email)
        self.assertEqual(customer_dict["first_name"], customer.first_name)

    @classmethod
    def deserialize(cls, data):
        """
        Deserializes a Customer from a dictionary
        """
        try:
            first_name = data["first_name"]
            last_name = data["last_name"]
            email = data["email"]
            password = data["password"]
            address = data["address"]

            if not cls._validate_email_format(email):
                raise DataValidationError(f"Invalid email format: '{email}'")

            return cls(
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password,
                address=address,
            )

        except KeyError as error:
            raise DataValidationError(
                f"Missing required field: {error.args[0]}"
            ) from error
        except TypeError as error:
            raise DataValidationError("Invalid input data") from error

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

        with self.assertRaises(DataValidationError) as context:
            Customer(**data)
        self.assertIn("missing first_name", str(context.exception).lower())

    def test_create_customer_missing_last_name(self):
        """It should raise DataValidationError if last name is missing"""
        data = CustomerFactory().serialize()
        data.pop("last_name")

        with self.assertRaises(DataValidationError) as context:
            Customer(**data)
        self.assertIn("missing last_name", str(context.exception).lower())

    def test_create_customer_missing_password(self):
        """It should raise DataValidationError if password is missing"""
        data = CustomerFactory().serialize()
        data.pop("password")

        with self.assertRaises(DataValidationError) as context:
            Customer(**data)
        self.assertIn("missing password", str(context.exception).lower())

    def test_create_customer_missing_address(self):
        """It should raise DataValidationError if address is missing"""
        data = CustomerFactory().serialize()
        data.pop("address")

        with self.assertRaises(DataValidationError) as context:
            Customer(**data)
        self.assertIn("missing address", str(context.exception).lower())

    # --------- UPDATE TESTS --------- #
    def test_update_a_customer(self):
        """It should Update a Customer"""
        customer = CustomerFactory()
        logging.debug(customer)
        customer.id = None
        customer.create()
        logging.debug(customer)
        self.assertIsNotNone(customer.id)
        # Change it an save it
        customer.first_name = "k9"
        original_id = customer.id
        customer.update()
        self.assertEqual(customer.id, original_id)
        self.assertEqual(customer.first_name, "k9")
        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        customers = Customer.all()
        self.assertEqual(len(customers), 1)
        self.assertEqual(customers[0].id, original_id)
        self.assertEqual(customers[0].first_name, "k9")

    def test_update_no_id(self):
        """It should not Update a Customer with no id"""
        customer = CustomerFactory()
        logging.debug(customer)
        customer.id = None
        self.assertRaises(DataValidationError, customer.update)
