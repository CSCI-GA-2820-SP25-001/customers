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
from unittest.mock import patch
from wsgi import app
from service.common import status
from service.models import db, Customer
from .factories import CustomerFactory
from service.routes import get_customers  # Add this import at the top


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

        data = resp.get_json()
        self.assertIsNotNone(data)
        self.assertIn("message", data)
        self.assertEqual(data["message"], "Welcome to the Customer API")

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

    # def test_internal_server_error(self):
    #     """It should return 500 Internal Server Error"""
    #     with patch("service.models.Customer.find", side_effect=Exception("boom")):
    #         response = self.client.get(f"{BASE_URL}/123", follow_redirects=True)
    #         self.assertEqual(
    #             response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR
    #         )
    #         data = response.get_json()
    #         self.assertEqual(data["error"], "Internal Server Error")
    #         self.assertIn("boom", data["message"])

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
            response, status_code = get_customers(customer.id)
            self.assertEqual(status_code, 200)

    def test_call_get_customers_directly(self):
        """It should directly call get_customers to trigger line 116"""
        customer = self._create_customers(1)[0]
        with app.test_request_context():
            response, code = get_customers(customer.id)
            self.assertEqual(code, status.HTTP_200_OK)
            self.assertEqual(response.get_json()["id"], customer.id)

    # ----------------------------------------------------------
    # TEST GET / QUERY
    # ----------------------------------------------------------

    # def test_query_customers_by_first_name(self):
    #     """It should return customers filtered by first_name query param"""
    #     customer = CustomerFactory(first_name="Zelda")
    #     customer.create()
    #     response = self.client.get("/customers", query_string={"first_name": "Zelda"})
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTrue(b"Zelda" in response.data)

    # def test_query_customers_by_address(self):
    #     """It should return customers filtered by address query param"""
    #     customer = CustomerFactory(address="123 Rainbow Road")
    #     customer.create()
    #     response = self.client.get(
    #         "/customers", query_string={"address": "123 Rainbow Road"}
    #     )
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTrue(b"123 Rainbow Road" in response.data)

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

    #  ----------------------------------------------------------
    # TEST LIST
    # ----------------------------------------------------------

    def test_get_customer_list(self):
        """It should Get a list of Customers"""
        self._create_customers(5)
        response = self.client.get(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 5)

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
