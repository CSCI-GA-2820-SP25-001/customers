"""
Models for Customer

All of the models are stored in this module
"""

import logging
import re
import enum
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum


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

    class StatusEnum(str, enum.Enum):
        """Class for the enumeration for the valid statuses for a Customer"""

        ACTIVE = "active"
        SUSPENDED = "suspended"
        DELETED = "deleted"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(63))
    last_name = db.Column(db.String(63))
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(63))
    address = db.Column(db.String(255))
    status = db.Column(Enum(StatusEnum), nullable=False, default=StatusEnum.ACTIVE)

    # Database auditing fields
    creation_date = db.Column(db.DateTime, default=db.func.now(), nullable=False)
    last_updated = db.Column(
        db.DateTime, default=db.func.now(), onupdate=db.func.now(), nullable=False
    )

    def __init__(self, **kwargs):
        kwargs.pop("id", None)
        try:
            self.first_name = kwargs.pop("first_name")
            self.last_name = kwargs.pop("last_name")
            self.email = kwargs.pop("email")
            self.password = kwargs.pop("password")
            self.address = kwargs.pop("address")
            status_str = kwargs.pop("status", "active")
            try:
                self.status = Customer.StatusEnum(status_str)
            except ValueError as exc:
                raise DataValidationError(f"Invalid status: {status_str}") from exc
        except KeyError as e:
            raise DataValidationError(f"missing {e.args[0]}") from e
        super().__init__(**kwargs)

        # require all fields
        # Validate required fields
        if self.first_name is None:
            raise DataValidationError("missing first_name")
        if self.last_name is None:
            raise DataValidationError("missing last_name")
        if self.email is None:
            raise DataValidationError("missing email")
        if self.password is None:
            raise DataValidationError("missing password")
        if self.address is None:
            raise DataValidationError("missing address")

    def __repr__(self):
        return f"<Customer {self.first_name} {self.last_name} id=[{self.id}]>"

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
            "status": self.status.value,
            "creation_date": (
                self.creation_date.isoformat() if self.creation_date else None
            ),
            "last_updated": (
                self.last_updated.isoformat() if self.last_updated else None
            ),
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

            try:
                status = Customer.StatusEnum(data["status"])
            except ValueError as exc:
                raise DataValidationError(f"Invalid status: {data['status']}") from exc

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
            status=status,
        )

    def update_from_dict(self, data):
        """Update fields of a Customer instance from a dictionary. Only update the fields provided in data."""
        if "first_name" in data:
            self.first_name = data["first_name"]
        if "last_name" in data:
            self.last_name = data["last_name"]
        if "email" in data:
            self.email = data["email"]
        if "password" in data:
            self.password = data["password"]
        if "address" in data:
            self.address = data["address"]
        if "status" in data:
            try:
                self.status = Customer.StatusEnum(data["status"])
            except ValueError as exc:
                raise DataValidationError(f"Invalid status: {data['status']}") from exc

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
        """Returns all Customers with the given first_name

        Args:
            name (string): the name of the Customers you want to match
        """
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.first_name == name)

    @staticmethod
    def _validate_email_format(email):
        """Validates email format using regex."""
        email_regex = r"(^[\w\.\+-]+@[\w-]+\.[a-zA-Z]{2,}$)"
        return re.match(email_regex, email) is not None

    @classmethod
    def filter_by_query(cls, **filters):
        """Filters customers based on query parameters (partial, case-insensitive)"""
        allowed_fields = [
            "first_name",
            "last_name",
            "email",
            "password",
            "address",
            "status",
        ]
        query = cls.query

        for field, value in filters.items():
            if field not in allowed_fields:
                raise DataValidationError(f"Invalid query field: {field}")

            # Special handling for status field which is an enum
            if field == "status":
                try:
                    # Convert to enum value for exact matching
                    status_enum = cls.StatusEnum(value)
                    query = query.filter(getattr(cls, field) == status_enum)
                except ValueError as exc:
                    raise DataValidationError(f"Invalid status value: {value}") from exc
            else:
                # For other fields, use case-insensitive partial match
                column = getattr(cls, field)
                query = query.filter(column.ilike(f"%{value}%"))

        return query.all()
