# CommerceCore Payment Service API

![RevPloy](Payment.png)
Welcome to the CommerceCore Payment Service API! This API provides payment endpoint for the CommerceCore API

## Table of Contents

1. [Getting Started](#getting-started)
2. [Installation](#installation)
3. [Usage](#usage)
4. [Testing](#testing)
5. [API Documentation](#api-documentation)
6. [License](#license)

## Getting Started

To get started with the CommerceCore Payment API, follow the instructions below to set up the project locally.

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/Backendly/commercecore-payment-service.git
   cd commercecore-payment-service
   ```

2. **Set up a virtual environment:**

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
   ```

3. **Install the dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure the database:**

   Ensure you have a PostgreSQL or MySQL database set up. Update the database settings in the `db.session.py` file.

   ```python
   DATABASE_URL = "postgresql://username:password@localhost/dbname"
   ```

   you can ignore the connect_args.

5. **Run the server:**

   ```bash
   uvicorn api.main:app --reload
   ```

## Usage

Once the server is running, you can interact with the API using tools like [Postman](https://www.postman.com/) or [curl](https://curl.se/).

## Testing

You can test the API endpoints using Postman. Import the collection directly using the following link:

[<img src="https://run.pstmn.io/button.svg" alt="Run In Postman" style="width: 128px; height: 32px;">](https://documenter.getpostman.com/view/36378381/2sAXqtb23V#intro)

## API Documentation

For detailed API documentation, visit the [Postman](https://documenter.getpostman.com/view/36378381/2sAXqtb23V#intro) endpoints.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
