######################################################################
# Copyright 2016, 2024 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# you may obtain a copy of the License at
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
Customer Service

This service implements a REST API that allows you to Create, Read, Update
and Delete Customer
"""

from flask import jsonify, request, url_for, abort
from flask import current_app as app  # Import Flask application
from service.models import Customer
from service.common import status  # HTTP Status Codes


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    return jsonify(message="Welcome to the Customer API"), 200


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################


######################################################################
# CREATE A NEW CUSTOMER
######################################################################
@app.route("/customers", methods=["POST"])
def create_customers():
    """
    Create a Customer
    This endpoint will create a Customer based the data in the body that is posted
    """
    app.logger.info("Request to Create a Customer...")
    check_content_type("application/json")

    data = request.get_json()
    app.logger.info("Processing: %s", data)
    customer = Customer.deserialize(data)

    # Save the new Customer to the database
    customer.create()
    app.logger.info("Customer with new id [%s] saved!", customer.id)

    # Return the location of the new Customer
    location_url = url_for("get_customers", customer_id=customer.id, _external=True)

    return (
        jsonify(customer.serialize()),
        status.HTTP_201_CREATED,
        {"Location": location_url},
    )


######################################################################
# READ A CUSTOMER
######################################################################
@app.route("/customers/<int:customer_id>", methods=["GET"])
def get_customers(customer_id):
    """
    Retrieve a single Customer

    This endpoint will return a Customer based on its id
    """
    app.logger.info("Request to Retrieve a customer with id [%s]", customer_id)

    # Attempt to find the Customer and abort if not found
    customer = Customer.find(customer_id)
    if not customer:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Customer with id '{customer_id}' was not found.",
        )

    app.logger.info(
        "Returning customer: %s + %s", customer.first_name, customer.last_name
    )
    return jsonify(customer.serialize()), status.HTTP_200_OK


######################################################################
# UPDATE AN EXISTING CUSTOMER
######################################################################
@app.route("/customers/<int:customer_id>", methods=["PUT"])
def update_customers(customer_id):
    """
    Update a Customer

    This endpoint will update a Customer based the body that is posted
    """
    app.logger.info("Request to Update a customer with id [%s]", customer_id)
    check_content_type("application/json")

    # Attempt to find the Customer and abort if not found
    customer = Customer.find(customer_id)
    if not customer:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Customer with id '{customer_id}' was not found.",
        )

    # Update the Customer with the new data
    data = request.get_json()
    app.logger.info("Processing: %s", data)
    customer.update_from_dict(data)

    # Save the updates to the database
    customer.update()

    app.logger.info("Customer with ID: %d updated.", customer.id)
    return jsonify(customer.serialize()), status.HTTP_200_OK


#####################################################################
# LIST ALL CUSTOMERS
######################################################################
@app.route("/customers", methods=["GET"])
def list_customers():
    """Returns all of the Customers"""
    app.logger.info("Request for customer list")

    customers = []

    # Parse any arguments from the query string
    first_name = request.args.get("first_name")
    last_name = request.args.get("last_name")
    email = request.args.get("email")
    password = request.args.get("password")
    address = request.args.get("address")

    if first_name:
        app.logger.info("Find by first name: %s", first_name)
        customers = Customer.find_by_first_name(first_name)
    elif last_name:
        app.logger.info("Find by last name: %s", last_name)
        customers = Customer.find_by_last_name(last_name)
    elif email:
        app.logger.info("Find by email: %s", email)
        customers = Customer.find_by_email(email)
    elif password:
        app.logger.info("Find by password: %s", password)
        customers = Customer.find_by_password(password)
    elif address:
        app.logger.info("Find by address: %s", address)
        customers = Customer.find_by_address(address)
    else:
        app.logger.info("Find all")
        customers = Customer.all()

    results = [customer.serialize() for customer in customers]
    app.logger.info("Returning %d customers", len(results))
    return jsonify(results), status.HTTP_200_OK


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


# ---------------------------------------------------------------------
# Checks the ContentType of a request
# ---------------------------------------------------------------------
def check_content_type(content_type) -> None:
    """Checks that the media type is correct"""
    if "Content-Type" not in request.headers:
        app.logger.error("No Content-Type specified.")
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {content_type}",
        )

    if request.headers["Content-Type"] == content_type:
        return

    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {content_type}",
    )


@app.route("/error")
def trigger_error():
    """This route is only used to test 500 error handler"""
    raise RuntimeError("This is a test error for HTTP 500")


######################################################################
# DELETE A CUSTOMER
######################################################################
@app.route("/customers/<int:customers_id>", methods=["DELETE"])
def delete_customers(customers_id):
    """
    Delete a Customer

    This endpoint will delete a Customer based the id specified in the path
    """
    app.logger.info("Request to Delete a customers with id [%s]", customers_id)

    # Delete the Customer if it exists
    customers = Customer.find(customers_id)
    if customers:
        app.logger.info("Customers with ID: %d found.", customers.id)
        customers.delete()

    app.logger.info("Customers with ID: %d delete complete.", customers_id)
    return {}, status.HTTP_204_NO_CONTENT
