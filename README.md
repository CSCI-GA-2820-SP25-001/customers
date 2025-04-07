# Customers Service

[![Build Status](https://github.com/CSCI-GA-2820-SP25-001/customers/actions/workflows/workflow.yml/badge.svg)](https://github.com/CSCI-GA-2820-SP25-001/customers/actions)
[![codecov](https://codecov.io/gh/CSCI-GA-2820-SP25-001/customers/graph/badge.svg?token=NQMF0BD24D)](https://codecov.io/gh/CSCI-GA-2820-SP25-001/customers)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Language-Python-blue.svg)](https://python.org/)

### Codecov (badge)
This project uses [Codecov](https://about.codecov.io/) to track unit test coverage as part of our Continuous Integration (CI) pipeline. Every Pull Request is automatically tested, and coverage reports are uploaded to Codecov to ensure code quality and maintain 95%+ test coverage.

[![codecov](https://codecov.io/gh/CSCI-GA-2820-SP25-001/customers/graph/badge.svg?token=ZADCYPUSA4)](https://codecov.io/gh/CSCI-GA-2820-SP25-001/customers)

## Overview
The **Customers Service** is a microservice that represents customer accounts for an eCommerce platform. This service provides CRUD operations to manage customer information, including first name, last name, email, password, and address.

## Setup Instructions

### Prerequisites
Ensure you have the following installed on your system:
- Python (>=3.8)
- pip (Python package manager)
- Flask
- PostgreSQL (if using a database)


### Installation
1. Clone the repository:
   ```sh
   git clone <repository-url>
   cd customers-service
   ```
2. Create and activate a virtual environment:
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
4. Set up environment variables:
   ```sh
   cp dot-env-example .env
   ```
   Update `.env` with necessary configurations.
5. Initialize the database:
   ```sh
   flask db init
   flask db migrate
   flask db upgrade
   ```

## Usage Guide

### API Endpoints

#### Create a Customer
**POST** `/customers`
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john.doe@example.com",
  "password": "securepassword",
  "address": "123 Main St, Springfield"
}
```

#### Retrieve a Customer
**GET** `/customers/{id}`

#### Update a Customer
**PUT** `/customers/{id}`
```json
{
  "first_name": "Jane"
}
```

#### Delete a Customer
**DELETE** `/customers/{id}`

## Running Tests
To run unit tests:
```sh
python -m unittest discover tests
```

## Project Structure
The project contains the following directories and files:

```text
.gitignore          - this will ignore vagrant and other metadata files
.flaskenv           - Environment variables to configure Flask
.gitattributes      - File to fix Windows CRLF issues
.devcontainers/     - Folder with support for VSCode Remote Containers
dot-env-example     - copy to .env to use environment variables
pyproject.toml      - Poetry list of Python libraries required by your code

service/                   - service python package
├── __init__.py            - package initializer
├── config.py              - configuration parameters
├── models.py              - module with business models
├── routes.py              - module with service routes
└── common                 - common code package
    ├── cli_commands.py    - Flask command to recreate all tables
    ├── error_handlers.py  - HTTP error handling code
    ├── log_handlers.py    - logging setup code
    └── status.py          - HTTP status constants

tests/                     - test cases package
├── __init__.py            - package initializer
├── factories.py           - Factory for testing with fake objects
├── test_cli_commands.py   - test suite for the CLI
├── test_models.py         - test suite for business models
└── test_routes.py         - test suite for service routes
```

## Deployment
To deploy the service, ensure you have:
- A production-ready database (e.g., PostgreSQL, MySQL)
- Environment variables set for production

Deployment steps may vary based on the hosting provider (Heroku, AWS, etc.).

## Contribution Guidelines
1. Fork the repository
2. Create a feature branch (`git checkout -b feature-xyz`)
3. Commit changes (`git commit -m 'Add new feature'`)
4. Push to branch (`git push origin feature-xyz`)
5. Open a Pull Request

## License

Copyright (c) 2016, 2025 [John Rofrano](https://www.linkedin.com/in/JohnRofrano/). All rights reserved.

Licensed under the Apache License. See [LICENSE](LICENSE)

This repository is part of the New York University (NYU) masters class: **CSCI-GA.2820-001 DevOps and Agile Methodologies** created and taught by [John Rofrano](https://cs.nyu.edu/~rofrano/), Adjunct Instructor, NYU Courant Institute, Graduate Division, Computer Science, and NYU Stern School of Business.

## Contact & Support
For any issues, create a GitHub issue or contact the maintainers.
