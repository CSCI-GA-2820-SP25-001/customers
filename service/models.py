"""
Models for Customer

All of the models are stored in this module
"""

import logging
import re
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


class DataValidationError(Exception):
    """Used for an data validation errors when deserializing"""


class Customer(db.Model):
    """
    Class that represents a Customer
    """

    ##################################################
    # Table Schema
    ##################################################

    # First Name
    # Last Name
    # Customer ID (unique)
    # Email (unique)
    # Password
    # Address (one string)
    # creation date

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(63))
    last_name = db.Column(db.String(63))
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(63))
    address = db.Column(db.String(255))

    # Database auditing fields
    creation_date = db.Column(db.DateTime, default=db.func.now(), nullable=False)
    last_updated = db.Column(
        db.DateTime, default=db.func.now(), onupdate=db.func.now(), nullable=False
    )

    def __init__(self, **kwargs):
        self.first_name = kwargs.get("first_name")
        self.last_name = kwargs.get("last_name")
        self.email = kwargs.get("email")
        self.password = kwargs.get("password")
        self.address = kwargs.get("address")

    def __repr__(self):
        return f"<Customer {self.name} id=[{self.id}]>"

    def create(self):
        """
        Creates a Customer in the database
        Raises DataValidationError if email already exists or has invalid format
        """
        logger.info("Creating customer %s %s", self.first_name, self.last_name)
        self.id = None  # ensure db generates the ID

        # Validate email format explicitly
        if not self._validate_email_format(self.email):
            raise DataValidationError(f"Invalid email format: '{self.email}'")

        existing_customer = Customer.query.filter_by(email=self.email).first()
        if existing_customer:
            raise DataValidationError(
                f"Customer with email '{self.email}' already exists."
            )

        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error creating customer: %s", e)
            raise DataValidationError(
                "Could not create customer due to a database error."
            ) from e

    def update(self):
        """
        Updates a Customer in the database.
        Raises a DataValidationError if the Customer does not have an ID.
        """
        if self.id is None:
            raise DataValidationError("Cannot update Customer without an ID.")

        logger.info("Saving %s", self.first_name)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error updating record: %s", self)
            raise DataValidationError(
                f"Database error while updating customer: {e}"
            ) from e

    def delete(self):
        """Removes a Customer from the data store"""
        logger.info("Deleting %s", self.first_name)
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error deleting record: %s", self)
            raise DataValidationError(e) from e

    def serialize(self):
        """Serializes a Customer into a dictionary"""
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "address": self.address,
            "password": self.password,
        }

    @classmethod
    def deserialize(cls, data):
        """
        Deserializes a Customer from a dictionary and validates email format.

        Args:
            data (dict): A dictionary containing the customer data
        """
        try:
            first_name = data["first_name"]
            last_name = data["last_name"]
            email = data["email"]
            password = data["password"]
            address = data["address"]

            if not cls._validate_email_format(email):
                raise DataValidationError(f"Invalid email format: '{email}'")

        except AttributeError as error:
            raise DataValidationError("Invalid attribute: " + error.args[0]) from error
        except KeyError as error:
            raise DataValidationError(
                "Invalid Customer: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError("Invalid input data") from error

        return cls(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
            address=address,
        )

    ##################################################
    # CLASS METHODS
    ##################################################

    @classmethod
    def all(cls):
        """Returns all of the Customers in the database"""
        logger.info("Processing all Customers")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """Finds a Customer by it's ID"""
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.session.get(cls, by_id)

    @classmethod
    def find_by_name(cls, name):
        """Returns all Customers with the given name

        Args:
            name (string): the name of the Customers you want to match
        """
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.name == name)

    @staticmethod
    def _validate_email_format(email):
        """Validates email format using regex."""
        email_regex = r"(^[\w\.\+-]+@[\w-]+\.[a-zA-Z]{2,}$)"
        return re.match(email_regex, email) is not None
