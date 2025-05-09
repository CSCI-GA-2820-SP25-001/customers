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
TestCustomer API Service Test Suite
"""

# pylint: disable=duplicate-code
import os
import logging
from unittest import TestCase

# from unittest.mock import patch
from wsgi import app
from service.common import status
from service.models import db, Customer
from service.routes import get_customers  # Add this import at the top
from service import create_app
from .factories import CustomerFactory


DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)
BASE_URL = "/customers"


######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestCustomerService(TestCase):
    """REST API Server Tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """Run once after all tests"""
        db.session.close()

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()
        db.session.query(Customer).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ############################################################
    # Utility function to bulk create customers
    ############################################################
    def _create_customers(self, count: int = 1) -> list:
        """Factory method to create customers in bulk"""
        customers = []
        for _ in range(count):
            test_customer = CustomerFactory()
            response = self.client.post(BASE_URL, json=test_customer.serialize())
            self.assertEqual(
                response.status_code,
                status.HTTP_201_CREATED,
                "Could not create test customer",
            )
            new_customer = response.get_json()
            test_customer.id = new_customer["id"]
            customers.append(test_customer)
        return customers

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """It should call the home page and check the response"""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        # Check that the response is HTML
        self.assertIn("text/html", resp.content_type)
        # Check that the HTML contains the expected content
        self.assertIn(b"Customer Demo REST API Service", resp.data)

    def test_method_not_allowed(self):
        """It should return 405 Method Not Allowed"""
        response = self.client.put("/")  # PUT not allowed on root
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_bad_request(self):
        """It should return 400 Bad Request"""
        # Force Flask to raise a 400 — e.g., by sending bad JSON
        response = self.client.post(
            BASE_URL, data="{bad json", content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_internal_server_error(self):
        """It should return 500 Internal Server Error"""
        app.config["PROPAGATE_EXCEPTIONS"] = (
            False  # this line tells Flask to use error handler
        )
        response = self.client.get("/error")
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        data = response.get_json()
        self.assertEqual(data["error"], "Internal Server Error")
        self.assertIn("Internal Server Error", data["message"])

    def test_trigger_validation_error(self):
        """It should return 400 from DataValidationError handler"""
        # Create an invalid payload missing a required field
        bad_payload = {"email": "bad@example.com"}  # missing first_name, etc.
        response = self.client.post(BASE_URL, json=bad_payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.get_json()
        self.assertEqual(data["error"], "Bad Request")

    def test_logging_formatter_is_set(self):
        """It should apply the logging formatter to all handlers"""

        created_app = create_app()
        for handler in created_app.logger.handlers:
            assert handler.formatter is not None  # formatter was applied

    # ----------------------------------------------------------
    # TEST CREATE
    # ----------------------------------------------------------
    def test_create_customer(self):
        """It should Create a new Customer"""
        test_customer = CustomerFactory()
        logging.debug("Test Customer: %s", test_customer.serialize())
        response = self.client.post(BASE_URL, json=test_customer.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = response.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_customer = response.get_json()
        self.assertEqual(new_customer["first_name"], test_customer.first_name)
        self.assertEqual(new_customer["last_name"], test_customer.last_name)
        self.assertEqual(new_customer["email"], test_customer.email)
        self.assertEqual(new_customer["password"], test_customer.password)
        self.assertEqual(new_customer["address"], test_customer.address)

        # Check that the location header was correct
        response = self.client.get(location)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        new_customer = response.get_json()
        self.assertEqual(new_customer["first_name"], test_customer.first_name)
        self.assertEqual(new_customer["last_name"], test_customer.last_name)
        self.assertEqual(new_customer["email"], test_customer.email)
        self.assertEqual(new_customer["password"], test_customer.password)
        self.assertEqual(new_customer["address"], test_customer.address)

    def test_create_customer_no_content_type(self):
        """It should fail to create a customer if Content-Type is missing"""
        response = self.client.post(BASE_URL, data="{}")  # no content_type set
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
        data = response.get_json()
        self.assertIn("Content-Type must be application/json", data["message"])

    def test_create_customer_wrong_content_type(self):
        """It should fail to create a customer if Content-Type is incorrect"""
        response = self.client.post(BASE_URL, data="{}", content_type="text/plain")
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
        data = response.get_json()
        self.assertIn("Content-Type must be application/json", data["message"])

    # ----------------------------------------------------------
    # TEST READ
    # ----------------------------------------------------------

    def test_get_customer(self):
        """It should Get a single Customer"""
        # get the id of a customer
        test_customer = self._create_customers(1)[0]
        response = self.client.get(f"{BASE_URL}/{test_customer.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["first_name"], test_customer.first_name)
        self.assertEqual(data["last_name"], test_customer.last_name)

    def test_get_customer_not_found(self):
        """It should not Get a Customer thats not found"""
        response = self.client.get(f"{BASE_URL}/0")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        logging.debug("Response data = %s", data)
        self.assertIn("was not found", data["message"])

    def test_get_deleted_customer(self):
        """It should return 404 when trying to GET a deleted customer"""
        # Create a customer and delete it
        customer = self._create_customers(1)[0]
        del_response = self.client.delete(f"{BASE_URL}/{customer.id}")
        self.assertEqual(del_response.status_code, status.HTTP_204_NO_CONTENT)

        # Try to GET the deleted customer
        get_response = self.client.get(f"{BASE_URL}/{customer.id}")
        self.assertEqual(get_response.status_code, status.HTTP_404_NOT_FOUND)
        data = get_response.get_json()
        self.assertIn("was not found", data["message"])

    def test_direct_call_to_get_customers(self):
        """[DEBUG] Directly call get_customers() to trigger line 116"""
        customer = self._create_customers(1)[0]
        with app.test_request_context():  # Needed for jsonify to work
            _, status_code = get_customers(customer.id)
            self.assertEqual(status_code, 200)

    def test_call_get_customers_directly(self):
        """It should directly call get_customers to trigger line 116"""
        customer = self._create_customers(1)[0]
        with app.test_request_context():
            response, code = get_customers(customer.id)
            self.assertEqual(code, status.HTTP_200_OK)
            self.assertEqual(response.get_json()["id"], customer.id)

    # ----------------------------------------------------------
    # TEST UPDATE
    # ----------------------------------------------------------
    def test_update_customer(self):
        """It should Update an existing Customer"""
        # create a customer to update
        test_customer = CustomerFactory()
        response = self.client.post(BASE_URL, json=test_customer.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # update the customer
        new_customer = response.get_json()
        logging.debug(new_customer)
        new_customer["first_name"] = "unknown"
        response = self.client.put(
            f"{BASE_URL}/{new_customer['id']}", json=new_customer
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_customer = response.get_json()
        self.assertEqual(updated_customer["first_name"], "unknown")

    def test_update_nonexistent_customer(self):
        """It should return 404 when trying to update a non-existent customer"""
        fake_id = 999999
        update_data = {
            "first_name": "Ghost",
            "last_name": "User",
            "email": "ghost@example.com",
            "password": "invisible123",
            "address": "404 Nowhere Lane",
            "status": "active",
        }

        response = self.client.put(
            f"{BASE_URL}/{fake_id}",
            json=update_data,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        self.assertIn("was not found", data["message"])

    #  ----------------------------------------------------------
    # TEST LIST / QUERY
    # ----------------------------------------------------------

    def test_get_customer_list(self):
        """It should Get a list of Customers"""
        self._create_customers(5)
        response = self.client.get(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 5)

    def test_list_customers_no_filters(self):
        """It should return all customers when no filters are provided"""
        self._create_customers(3)  # Create 3 customers
        response = self.client.get(BASE_URL)  # No query parameters
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 3)

    def test_list_customers_filter_by_first_name(self):
        """It should return customers matching partial first_name (case-insensitive)"""
        customer_1 = CustomerFactory(first_name="Alice", last_name="Smith")
        customer_2 = CustomerFactory(first_name="Alina", last_name="Smythe")
        customer_3 = CustomerFactory(first_name="Bob", last_name="Jones")
        for customer in [customer_1, customer_2, customer_3]:
            response = self.client.post(BASE_URL, json=customer.serialize())
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Filter by partial, case-insensitive match on first_name
        response = self.client.get(BASE_URL, query_string={"first_name": "ali"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.get_json()
        self.assertEqual(len(results), 2)
        self.assertTrue(any("Alice" in c["first_name"] for c in results))
        self.assertTrue(any("Alina" in c["first_name"] for c in results))

    def test_list_customers_filter_by_last_name(self):
        """It should return customers matching partial last_name (case-insensitive)"""
        c1 = CustomerFactory(last_name="Johnson")
        c2 = CustomerFactory(last_name="Johnston")
        c3 = CustomerFactory(last_name="Doe")
        for c in [c1, c2, c3]:
            self.client.post(BASE_URL, json=c.serialize())

        response = self.client.get(BASE_URL, query_string={"last_name": "john"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.get_json()
        self.assertEqual(len(results), 2)
        self.assertTrue(all("john" in c["last_name"].lower() for c in results))

    def test_list_customers_filter_by_email(self):
        """It should return customers matching partial email (case-insensitive)"""
        c1 = CustomerFactory(email="alice@example.com")
        c2 = CustomerFactory(email="bob@example.com")
        c3 = CustomerFactory(email="support@another.com")
        for c in [c1, c2, c3]:
            self.client.post(BASE_URL, json=c.serialize())

        response = self.client.get(BASE_URL, query_string={"email": "example"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.get_json()
        self.assertEqual(len(results), 2)
        self.assertTrue(all("example" in c["email"] for c in results))

    def test_list_customers_filter_by_address(self):
        """It should return customers matching partial address (case-insensitive)"""
        c1 = CustomerFactory(address="123 Rainbow Lane")
        c2 = CustomerFactory(address="456 Rainstorm Blvd")
        c3 = CustomerFactory(address="789 Sunshine St")
        for c in [c1, c2, c3]:
            self.client.post(BASE_URL, json=c.serialize())

        response = self.client.get(BASE_URL, query_string={"address": "rain"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.get_json()
        self.assertEqual(len(results), 2)
        self.assertTrue(all("rain" in c["address"].lower() for c in results))

    def test_list_customers_filter_by_password(self):
        """It should return customers matching partial password (case-insensitive)"""
        c1 = CustomerFactory(password="SuperSecret123")
        c2 = CustomerFactory(password="superman456")
        c3 = CustomerFactory(password="notmatching")
        for c in [c1, c2, c3]:
            self.client.post(BASE_URL, json=c.serialize())

        response = self.client.get(BASE_URL, query_string={"password": "super"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.get_json()
        self.assertEqual(len(results), 2)
        self.assertTrue(all("super" in c["password"].lower() for c in results))

    def test_list_customers_filter_by_multiple_fields(self):
        """It should return customers matching multiple fields (case-insensitive)"""
        c1 = CustomerFactory(first_name="Alice", last_name="Johnson")
        c2 = CustomerFactory(first_name="Alicia", last_name="Johnson")
        c3 = CustomerFactory(first_name="Alice", last_name="Smith")
        c4 = CustomerFactory(first_name="Bob", last_name="Johnson")
        for c in [c1, c2, c3, c4]:
            self.client.post(BASE_URL, json=c.serialize())

        response = self.client.get(
            BASE_URL, query_string={"first_name": "ali", "last_name": "john"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.get_json()

        # Expecting c1 and c2 only
        self.assertEqual(len(results), 2)
        for result in results:
            self.assertIn("ali", result["first_name"].lower())
            self.assertIn("john", result["last_name"].lower())

    def test_list_customers_invalid_filter_param(self):
        """It should return 400 when an invalid query parameter is provided"""
        response = self.client.get(BASE_URL, query_string={"invalid_param": "whatever"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.get_json()
        self.assertIn("Invalid", data["message"])

    # ----------------------------------------------------------
    # TEST DELETE
    # ----------------------------------------------------------
    def test_delete_customers(self):
        """It should Delete a Customer"""
        test_customers = self._create_customers(1)[0]
        response = self.client.delete(f"{BASE_URL}/{test_customers.id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.data), 0)
        # make sure they are deleted
        response = self.client.get(f"{BASE_URL}/{test_customers.id}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_non_existing_customers(self):
        """It should Delete a Customer even if it doesn't exist"""
        response = self.client.delete(f"{BASE_URL}/0")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.data), 0)

    # ----------------------------------------------------------
    # TEST STATEFUL ACTION
    # ----------------------------------------------------------

    def test_activate_customer(self):
        """It should activate a suspended Customer"""
        customer = self._create_customers(1)[0]

        # First suspend the customer using the endpoint (safer and guaranteed to persist)
        response = self.client.put(
            f"{BASE_URL}/{customer.id}/action",
            json={"action": "suspend"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["status"], "suspended")

        # Now activate the same customer
        response = self.client.put(
            f"{BASE_URL}/{customer.id}/action",
            json={"action": "activate"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["status"], "active")

    def test_suspend_customer(self):
        """It should suspend an active Customer"""
        customer = self._create_customers(1)[0]

        response = self.client.put(
            f"{BASE_URL}/{customer.id}/action",
            json={"action": "suspend"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["status"], "suspended")

    def test_idempotent_action(self):
        """It should not change status if already in desired state"""
        customer = self._create_customers(1)[0]

        response = self.client.put(
            f"{BASE_URL}/{customer.id}/action",
            json={"action": "activate"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["status"], "active")  # Still active

    def test_action_missing_field(self):
        """It should return 400 when action is missing"""
        customer = self._create_customers(1)[0]

        response = self.client.put(
            f"{BASE_URL}/{customer.id}/action",
            json={},  # missing "action"
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.get_json()
        self.assertIn("Invalid action", data["message"])

    def test_action_invalid_value(self):
        """It should return 400 for invalid action"""
        customer = self._create_customers(1)[0]

        response = self.client.put(
            f"{BASE_URL}/{customer.id}/action",
            json={"action": "freeze"},  # unsupported action
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.get_json()
        self.assertIn("Invalid action", data["message"])

    def test_action_customer_not_found(self):
        """It should return 404 when Customer is not found"""
        response = self.client.put(
            f"{BASE_URL}/999999/action",
            json={"action": "suspend"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        self.assertIn("was not found", data["message"])

    ######################################################################
    # HEALTH CHECK ENDPOINT FOR KUBERNETES (for CI)
    ######################################################################

    def test_health_check(self):
        """It should return 200 OK with {status: OK}"""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.get_json()["status"], "OK")
