# RepaySync

RepaySync is a Django-based system that centralizes customer interaction tracking between field collection teams and central calling teams for lending companies.

## Key Features

- **Hierarchical Role-Based Access Control**:

  - Super Managers: Full system access
  - Managers: Access to officers reporting to them (tree structure)
  - Collection Officers: Access to assigned customers only
  - Calling Agents: View all customers, add interactions

- **Customer Management**:

  - Customer profiles with branch and EMI paid status
  - Officer assignment
  - History of all interactions

- **Loan Processing**:

  - Create and manage loans
  - Loan approval workflow
  - Payment tracking
  - Loan restructuring and write-offs

- **Interactions**:
  - Record customer interactions (calls, visits)
  - Immutable history (interactions cannot be edited once created)
  - Schedule and track follow-ups

## Technology Stack

- Backend: Django 5.1 with Django REST Framework
- Database: PostgreSQL
- Authentication: JWT
- Containerization: Docker and Docker Compose

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Git

### Installation with Docker

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/RepaySync.git
   cd RepaySync
   ```

2. Start the application with Docker Compose:

   ```bash
   docker-compose up -d
   ```

3. Create a superuser:

   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

4. Access the application:
   - Admin interface: http://localhost:8000/admin/
   - API documentation: http://localhost:8000/api/docs/

### Local Development Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/RepaySync.git
   cd RepaySync
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/Scripts/activate  # Windows
   # source venv/bin/activate    # Linux/Mac
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Configure the environment variables (see `.env.example`).

5. Run migrations:

   ```bash
   python manage.py migrate
   ```

6. Create a superuser:

   ```bash
   python manage.py createsuperuser
   ```

7. Start the development server:
   ```bash
   python manage.py runserver
   ```

## Usage

See the detailed walkthrough in [walkthrough.md](walkthrough.md) for step-by-step instructions on how to use the system.

## API Documentation

- API endpoints are documented using Swagger and available at `/api/docs/`
- Authentication is handled via JWT tokens

## Implementation Notes

- Customer interactions are immutable records (cannot be edited/deleted once created)
- Hierarchical access is implemented as a tree structure where managers can see customers of officers reporting to them
- Customer EMI paid status can be updated by both field collection team and calling team

## Testing

Run tests with pytest:

```bash
pytest
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

[Nidhi Yashwanth](https://github.com/nidhiyashwanth)
