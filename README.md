# RepaySync - Loan Management System

RepaySync is a comprehensive loan collection management system that helps financial institutions and lenders manage their loan portfolios, track repayments, and streamline the collection process. Built with Django, Django REST Framework, and PostgreSQL, it provides a robust API for serving both web and mobile applications.

## Features

- **Role-Based Access Control:** Four distinct user roles (Super Manager, Manager, Collection Officer, Calling Agent) with appropriate permissions
- **Customer Management:** Track customer details, contact information, and loan history
- **Loan Management:** Create and manage loan applications, approvals, and repayments
- **Payment Tracking:** Record and monitor loan repayments
- **Interaction Logging:** Document all customer interactions (calls, meetings, emails, etc.)
- **Follow-Up Management:** Schedule and track follow-up actions
- **API-First Design:** RESTful API endpoints for all functionality
- **JWT Authentication:** Secure authentication with JSON Web Tokens
- **Documentation:** Comprehensive API documentation with Swagger

## Technology Stack

- **Backend:** Django 5.1, Django REST Framework 3.15
- **Database:** PostgreSQL
- **Authentication:** JWT using djangorestframework-simplejwt
- **API Documentation:** drf-yasg (Swagger/OpenAPI)
- **Development Tools:** Django Debug Toolbar
- **Containerization:** Docker, Docker Compose

## Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL
- Docker and Docker Compose (optional)

### Installation

1. Clone the repository:

   ```
   git clone https://github.com/yourusername/repaysync.git
   cd repaysync
   ```

2. Create a virtual environment and activate it:

   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:

   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file with the following content (adjust as needed):

   ```
   DEBUG=True
   SECRET_KEY=your-secret-key-here
   ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

   DB_ENGINE=django.db.backends.postgresql
   DB_NAME=repaysync
   DB_USER=repaysync
   DB_PASSWORD=repaysync098
   DB_HOST=localhost
   DB_PORT=5432
   ```

5. Set up the database:
   ```
   python manage.py setup_db
   ```

### Running with Docker

1. Build and start the Docker containers:

   ```
   docker-compose up -d
   ```

2. Access the application at http://localhost:8000

### Running Locally

1. Run the development server:

   ```
   python manage.py runserver
   ```

2. Access the application at http://localhost:8000

## API Documentation

The API documentation is available at:

- Swagger UI: `/api/docs/`
- ReDoc: `/api/redoc/`

## Default Users

The system comes with the following default users for testing purposes:

- **Super Manager**:

  - Username: `admin`
  - Password: `password`

- **Manager**:

  - Username: `manager1`
  - Password: `password`

- **Collection Officer**:

  - Username: `officer1`
  - Password: `password`

- **Calling Agent**:
  - Username: `agent1`
  - Password: `password`

## License

This project is proprietary.

## Author

[Nidhi Yashwanth](https://github.com/nidhiyashwanth)
