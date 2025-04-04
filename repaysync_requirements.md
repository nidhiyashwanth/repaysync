# RepaySync Project Requirements Document

## 1. Project Overview

RepaySync is a Django-based backend system that centralizes customer interaction tracking between field collection teams and central calling teams for lending companies. The system will maintain comprehensive conversation history, implement role-based access controls, and provide dashboards for monitoring collection activities.

## 2. Technical Stack

- **Backend Framework**: Django 5.1
- **Database**: PostgreSQL 17.4
- **Authentication**: Django REST Framework with JWT
- **API Documentation**: Swagger/OpenAPI
- **Logging**: Django built-in logging + custom request-response logging
- **Testing**: pytest
- **Deployment**: Docker and Docker Compose (for development)

## 3. Data Models

### Users and Authentication

- User (extends Django AbstractUser)

  - Email
  - Phone
  - Role (Collection Officer, Manager, Super Manager, Calling Agent)
  - Active status
  - Created/Updated timestamps

- Hierarchy
  - Manager (ForeignKey to User)
  - Collection Officer (ForeignKey to User)
  - Created/Updated timestamps

### Customers and Loans

- Customer

  - Name
  - Contact details (phone, email, address)
  - Branch (according to interviewer clarification)
  - EMI Paid status (Boolean, default: not paid)
  - ID proof details
  - Status (Active/Inactive)
  - Created/Updated timestamps

- Loan

  - Customer (ForeignKey)
  - Loan amount
  - Outstanding amount
  - Loan date
  - Due date
  - Status (Active, Closed, Default)
  - Created/Updated timestamps

- CustomerAssignment
  - Customer (ForeignKey)
  - Collection Officer (ForeignKey to User)
  - Assignment date
  - Status (Active/Inactive)
  - Created/Updated timestamps

### Interactions

- Disposition (lookup table)

  - Name (Promise to Pay, Payment Received, Unreachable, Disputed, Will Pay Later, Wrong Number, etc.)
  - Category (Positive, Neutral, Negative)
  - Description
  - Active status

- CustomerInteraction

  - Customer (ForeignKey)
  - User (ForeignKey - who recorded the interaction)
  - Interaction type (Call, Visit)
  - Disposition (ForeignKey)
  - Comments
  - Next follow-up date
  - Interaction datetime
  - Created/Updated timestamps
  - Note: Interactions are immutable - once created, they cannot be modified (clarified by interviewer)

- Attachment (future extension)
  - Interaction (ForeignKey)
  - File
  - Description
  - Created/Updated timestamps

## 4. API Endpoints

### Authentication

- POST /api/auth/login/ - User login
- POST /api/auth/logout/ - User logout
- POST /api/auth/token/refresh/ - Refresh JWT token

### Users and Hierarchy

- GET /api/users/ - List users (filtered by role)
- POST /api/users/ - Create user
- GET /api/users/{id}/ - Retrieve user details
- PUT /api/users/{id}/ - Update user
- DELETE /api/users/{id}/ - Deactivate user (soft delete)
- POST /api/users/bulk-create/ - Bulk create users from CSV

### Customers

- GET /api/customers/ - List customers (with filters)
- POST /api/customers/ - Create customer
- GET /api/customers/{id}/ - Retrieve customer details
- PUT /api/customers/{id}/ - Update customer
- PATCH /api/customers/{id}/ - Partial update customer (e.g., to update paid status)
- DELETE /api/customers/{id}/ - Deactivate customer (soft delete)
- POST /api/customers/bulk-create/ - Bulk create customers from CSV

### Customer Assignments

- GET /api/assignments/ - List assignments
- POST /api/assignments/ - Create assignment
- PUT /api/assignments/{id}/ - Update assignment
- DELETE /api/assignments/{id}/ - Deactivate assignment
- POST /api/assignments/bulk-create/ - Bulk create assignments

### Interactions

- GET /api/interactions/ - List interactions (with filters)
- POST /api/interactions/ - Create interaction
- GET /api/interactions/{id}/ - Retrieve interaction details
- POST /api/interactions/bulk-create/ - Bulk create interactions from CSV
- Note: PUT, PATCH, and DELETE are intentionally excluded based on requirements

### Dispositions

- GET /api/dispositions/ - List all dispositions
- POST /api/dispositions/ - Create disposition
- PUT /api/dispositions/{id}/ - Update disposition

### Dashboard

- GET /api/dashboard/summary/ - Get summary statistics
- GET /api/dashboard/disposition-stats/ - Get disposition statistics
- GET /api/dashboard/team-performance/ - Get team performance metrics

## 5. Access Control

### Role-Based Permissions

- **Super Managers**: Full access to all customers, interactions, and users
- **Managers**: Access to all customers and interactions assigned to collection officers under them (directly or indirectly in a tree structure)
- **Collection Officers**: Access only to customers assigned to them
- **Calling Agents**: Access to all customers but cannot modify assignments

### Permission Rules

1. Only assigned collection officers, their managers, and super managers can update customer interactions for field visits
2. Any calling agent can contact and update interactions for any customer
3. Customer reassignment preserves historical interaction data
4. All users can view interaction history for customers they have access to
5. Interactions are immutable - once created, they cannot be modified or deleted

## 6. Bulk Operations

- CSV import for new users (collection officers, managers, calling agents)
- CSV import for new customers
- CSV import for customer assignments
- CSV import for bulk interaction updates
- CSV templates available for download

## 7. Logging

- All API requests and responses logged
- User actions tracked (login, logout, data modifications)
- Error logging with appropriate detail
- Audit trail for sensitive operations

## 8. Dashboards

- Latest disposition summary by customer
- Collection officer performance metrics
- Calling agent performance metrics
- Disposition breakdown charts
- Customer interaction timeline
- Follow-up calendar view

## 9. Implementation Phases

### Phase 1 (MVP)

- Core data models and database setup
- User authentication and role-based permissions
- Basic APIs for customer and interaction management
- Admin interface for system management

### Phase 2

- Bulk import/export functionality
- Advanced filtering and search
- Dashboard views
- Logging and audit functionality

### Phase 3

- Enhanced reporting
- Performance optimizations
- Extended API features
- File attachment support

## 10. Future Considerations

- Mobile application for field collection officers
- Automated notification system
- Integration with payment gateways
- Advanced analytics and reporting
- Machine learning for predicting customer payment behavior
