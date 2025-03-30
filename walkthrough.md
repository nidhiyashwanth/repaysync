# RepaySync Application Complete Walkthrough

This enhanced guide provides a detailed step-by-step walkthrough of the RepaySync loan management system with specific examples for testing all functionality.

## 1. Setup and Environment

### Prerequisites

- Python installed
- PostgreSQL installed and running
- Docker and Docker Compose (optional, for containerized setup)

### Installation

```bash
# Clone the repository (if not already done)
git clone <repository-url>
cd RepaySync

# Create and activate a virtual environment
python -m venv venv
source venv/Scripts/activate  # On Windows
# source venv/bin/activate    # On Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Verify the .env file contains proper database configuration:
# - DB_NAME=repaysync
# - DB_USER=repaysync
# - DB_PASSWORD=repaysync098
# - DB_HOST=localhost
# - DB_PORT=5432

# Run migrations
python manage.py migrate

# Create a superuser (use these exact credentials for following the guide)
python manage.py createsuperuser
# Username: admin
# Email: admin@repaysync.com
# Password: admin123456
```

## 2. User Roles and Permissions

RepaySync has a hierarchical permission system with four user roles:

| Role                   | Description               | Permissions                                                                                                                                                                                                                                  |
| ---------------------- | ------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Super Manager**      | Top-level administrator   | - Access to all system functions<br>- Create and manage all user types<br>- Approve/reject loans<br>- Write off loans<br>- View all reports and dashboards                                                                                   |
| **Manager**            | Department or branch head | - Manage Collection Officers and Calling Agents<br>- Review and approve loans<br>- Restructure loans<br>- Assign customers to officers<br>- View customers of officers reporting directly or indirectly to them<br>- View department reports |
| **Collection Officer** | Handles loan management   | - Create customer profiles<br>- Process loan applications<br>- Record payments<br>- Conduct customer interactions<br>- Manage follow-ups<br>- View only assigned customers                                                                   |
| **Calling Agent**      | Handles customer contact  | - View all active customers<br>- Record interactions (cannot edit/delete)<br>- Create follow-ups<br>- Limited view of customer data                                                                                                          |

### Hierarchical Access Control

The system implements a tree-based hierarchical access structure:

1. **Super Managers** can see all customers and interactions in the system
2. **Managers** can only see customers and interactions for Collection Officers who report to them (either directly or indirectly)
3. **Collection Officers** can only see customers assigned to them
4. **Calling Agents** can see all active customers but have read-only access

### Customer Updates

Both the field collection team (Collection Officers) and the central calling team (Calling Agents) can update customer interactions by adding new records. Note that:

1. Interactions once created cannot be modified or deleted
2. Each customer has a new field for branch and paid status (EMI paid status)
3. Both teams can update the paid status of customers

## 3. Start the Application

```bash
# Start the development server
python manage.py runserver
```

The application should now be running at http://127.0.0.1:8000/

## 4. Creating Test Users

Let's create a complete hierarchy of test users. Log in with the superuser account created earlier:

1. **Access the Admin Interface**

   - Navigate to http://127.0.0.1:8000/admin/
   - Log in with superuser credentials (nidhiyashwanth/supernidhi)
   - Go to Users > Add User

2. **Create a Manager User**

   - Username: manager1
   - Email: manager1@repaysync.com
   - Password: asidol304k3
   - First Name: John
   - Last Name: Manager
   - Role: MANAGER
   - Phone: +1234567890
   - Is staff: Checked
   - Is active: Checked

3. **Create a Collection Officer**

   - Username: officer1
   - Email: officer1@repaysync.com
   - Password: dndorl203e
   - First Name: Sarah
   - Last Name: Officer
   - Role: COLLECTION_OFFICER
   - Phone: +1234567891
   - Is staff: Checked
   - Is active: Checked

4. **Create a Calling Agent**
   - Username: agent1
   - Email: agent1@repaysync.com
   - Password: dkid9392kd
   - First Name: Alex
   - Last Name: Agent
   - Role: CALLING_AGENT
   - Phone: +1234567892
   - Is staff: Checked
   - Is active: Checked

## 5. Setting Up Hierarchy Relationships

The Hierarchy model defines reporting relationships between managers and collection officers:

1. **Create a Hierarchy Relationship**
   - Navigate to Users > Hierarchy > Add Hierarchy
   - Manager: Select "John Manager"
   - Collection Officer: Select "Sarah Officer"
   - Notes: "Main branch hierarchy"
   - Click Save

This establishes that Sarah Officer reports to John Manager.

## 6. Customer Management Workflow

### 6.1 Create a New Customer (as Collection Officer)

1. **Log in as the Collection Officer**

   - Log out of the admin account
   - Log in with officer1/dndorl203e

2. **Create a Customer**

   - Go to Customers > Add Customer
   - Fill in these details:
     - First Name: Michael
     - Last Name: Brown
     - Gender: MALE
     - Date of Birth: 1987-07-24
     - National ID: 2930494294903
     - Primary Phone: +1987654321
     - Email: michael.brown@example.com
     - City: San Francisco
     - State: CA
     - Country: US
     - Branch: North Branch
     - Paid Status: Unchecked (Not Paid)
     - Monthly Income: 5000.00
     - Assigned Officer: Sarah Officer (should be auto-selected)
     - Notes: New customer with good credit history
   - Click Save

3. **Create a Second Customer**
   - Add another customer with these details:
     - First Name: Emma
     - Last Name: Wilson
     - Gender: FEMALE
     - Date of Birth: 1995-09-03
     - National ID: 39474948392
     - Primary Phone: +1987654322
     - Email: emma.wilson@example.com
     - City: Los Angeles
     - State: CA
     - Country: US
     - Branch: South Branch
     - Paid Status: Unchecked (Not Paid)
     - Monthly Income: 4500.00
     - Assigned Officer: Sarah Officer
     - Notes: New customer referred by Michael Brown

## 7. Loan Management Workflow

### 7.1 Create a New Loan (as Collection Officer)

1. **Create a Loan for Michael Brown**

   - Go to Loans > Add Loan
   - Fill in these details:
     - Customer: Michael Brown
     - Loan Reference: (leave blank to auto-generate)
     - Status: PENDING
     - Principal Amount: 10000.00
     - Interest Rate: 12.00
     - Term Months: 12
     - Payment Frequency: MONTHLY
     - Assigned Officer: Sarah Officer
     - Notes: Home renovation loan
   - Click Save

2. **Create a Loan for Emma Wilson**
   - Add another loan with these details:
     - Customer: Emma Wilson
     - Loan Reference: (leave blank to auto-generate)
     - Status: PENDING
     - Principal Amount: 5000.00
     - Interest Rate: 10.00
     - Term Months: 6
     - Payment Frequency: MONTHLY
     - Assigned Officer: Sarah Officer
     - Notes: Personal loan for education

### 7.2 Approve a Loan (as Manager)

1. **Log in as the Manager**

   - Log out of the officer account
   - Log in with manager1/asidol304k3

2. **Review and Approve Michael's Loan**

   - Go to Loans and find Michael Brown's loan
   - Change the following:
     - Status: ACTIVE
     - Approval Date: (Today's date)
     - Disbursement Date: (Today's date)
     - First Payment Date: (1 month from today)
     - Maturity Date: (1 year from today)
   - Click Save

3. **Review and Approve Emma's Loan**
   - Find Emma Wilson's loan
   - Change the following:
     - Status: ACTIVE
     - Approval Date: (Today's date)
     - Disbursement Date: (Today's date)
     - First Payment Date: (1 month from today)
     - Maturity Date: (6 months from today)
   - Click Save

## 8. Payment Processing Workflow

### 8.1 Record a Payment (as Collection Officer)

1. **Log in as the Collection Officer**

   - Log out of the manager account
   - Log in with officer1/dndorl203e

2. **Record a Payment for Michael Brown's Loan**

   - Go to Payments > Add Payment
   - Fill in these details:
     - Loan: (Select Michael Brown's loan)
     - Payment Reference: (leave blank to auto-generate)
     - Amount: 1000.00
     - Payment Date: (Today's date)
     - Payment Method: CASH
     - Received By: Sarah Officer
     - Notes: First payment received
   - Click Save

3. **Verify Loan Update**

   - Go to Loans and check Michael Brown's loan
   - Verify the Amount Paid is updated to 1000.00
   - Verify the Last Payment Date is set to today
   - Verify the Remaining Balance is calculated correctly

4. **Update the Paid Status for the Customer**
   - Go to Customers and find Michael Brown
   - Change the Paid Status to "Checked" (Paid)
   - Click Save

### 8.2 Record Another Payment

1. **Record a Second Payment for Michael Brown's Loan**

   - Go to Payments > Add Payment
   - Fill in these details:
     - Loan: (Select Michael Brown's loan)
     - Payment Reference: (leave blank to auto-generate)
     - Amount: 1000.00
     - Payment Date: (Today's date)
     - Payment Method: BANK_TRANSFER
     - Received By: Sarah Officer
     - Notes: Second payment received
   - Click Save

2. **Verify Loan Update**
   - Check that Michael Brown's loan now shows 2000.00 as the Amount Paid
   - Verify the Remaining Balance has decreased accordingly

## 9. Interactions and Follow-ups Workflow

### 9.1 Record an Interaction (as Calling Agent)

1. **Log in as the Calling Agent**

   - Log out of the officer account
   - Log in with agent1/dkid9392kd

2. **Record a Call with Michael Brown**

   - Go to Interactions > Add Interaction
   - Fill in these details:
     - Customer: Michael Brown
     - Loan: (Select Michael Brown's loan)
     - Interaction Type: CALL
     - Start Time: (Current time)
     - End Time: (15 minutes after start time)
     - Contact Person: Michael Brown
     - Outcome: SUCCESSFUL
     - Notes: Called to remind about upcoming payment. Customer confirmed payment will be made next week.
     - Initiated By: Alex Agent
   - Click Save

3. **Try to Edit the Interaction**
   - Note that you cannot edit or delete the interaction once it's created
   - This is by design - interactions are immutable records

### 9.2 Create a Follow-up (as Calling Agent)

1. **Create a Follow-up Task from the Interaction**
   - From the interaction detail page, click "Add Follow-up"
   - Fill in these details:
     - Related Interaction: (Should be pre-filled)
     - Customer: Michael Brown
     - Scheduled Date: (1 week from today)
     - Scheduled Time: 10:00 AM
     - Description: Follow up on payment promise
     - Priority: MEDIUM
     - Assigned To: Sarah Officer
     - Status: PENDING
   - Click Save

### 9.3 Complete a Follow-up (as Collection Officer)

1. **Log in as the Collection Officer**

   - Log out of the agent account
   - Log in with officer1/dndorl203e

2. **Complete the Follow-up Task**
   - Go to Follow-ups and find the pending follow-up
   - Change the following:
     - Status: COMPLETED
     - Completion Date: (Today's date)
     - Completion Time: (Current time)
     - Result: Payment received as promised
   - Click Save

## 10. Loan Restructuring and Write-off Workflow

### 10.1 Restructure a Loan (as Manager)

1. **Log in as the Manager**

   - Log out of the officer account
   - Log in with manager1/asidol304k3

2. **Create a Loan to Restructure**

   - Go to Loans > Add Loan
   - Fill in these details:
     - Customer: Emma Wilson
     - Loan Reference: (leave blank to auto-generate)
     - Status: ACTIVE
     - Principal Amount: 3000.00
     - Interest Rate: 15.00
     - Term Months: 6
     - Payment Frequency: MONTHLY
     - Assigned Officer: Sarah Officer
     - Days Past Due: 45
     - Notes: Customer is having difficulty repaying
   - Click Save

3. **Restructure the Loan**
   - Edit the newly created loan
   - Change the following:
     - Status: RESTRUCTURED
     - Interest Rate: 10.00 (reduced)
     - Term Months: 12 (extended)
     - Days Past Due: 0 (reset)
     - Notes: Loan restructured due to financial hardship
   - Click Save

### 10.2 Write Off a Loan (as Super Manager)

1. **Log in as the Super Manager**

   - Log out of the manager account
   - Log in with nidhiyashwanth/supernidhi

2. **Create a Loan to Write Off**

   - Go to Loans > Add Loan
   - Fill in these details:
     - Customer: Michael Brown
     - Loan Reference: (leave blank to auto-generate)
     - Status: DEFAULTED
     - Principal Amount: 2000.00
     - Interest Rate: 12.00
     - Term Months: 6
     - Payment Frequency: MONTHLY
     - Assigned Officer: Sarah Officer
     - Days Past Due: 120
     - Notes: Customer unable to repay
   - Click Save

3. **Write Off the Loan**
   - Edit the defaulted loan
   - Change the following:
     - Status: WRITTEN_OFF
     - Notes: Loan written off due to non-recovery after 120 days
   - Click Save

## 11. API Testing

### 11.1 Get an Authentication Token

```bash
# Using curl to get a JWT token
curl -X POST http://127.0.0.1:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "nidhiyashwanth", "password": "supernidhi"}'
```

Save the access token returned for use in subsequent requests.

### 11.2 List Customers via API

```bash
# Get list of customers
curl -X GET http://127.0.0.1:8000/api/customers/ \
  -H "Authorization: Bearer <your_access_token>"
```

### 11.3 Create a Customer via API

```bash
# Create a new customer
curl -X POST http://127.0.0.1:8000/api/customers/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_access_token>" \
  -d '{
    "first_name": "API",
    "last_name": "Customer",
    "gender": "MALE",
    "primary_phone": "+1122334455",
    "email": "api.customer@example.com",
    "city": "API City",
    "assigned_officer": 3
  }'
```

### 11.4 Create a Loan via API

```bash
# Create a new loan
curl -X POST http://127.0.0.1:8000/api/loans/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_access_token>" \
  -d '{
    "customer": 1,
    "principal_amount": "7500.00",
    "interest_rate": "11.50",
    "term_months": 9,
    "assigned_officer": 3
  }'
```

### 11.5 Record a Payment via API

```bash
# Record a payment
curl -X POST http://127.0.0.1:8000/api/payments/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_access_token>" \
  -d '{
    "loan": 1,
    "amount": "850.00",
    "payment_date": "2025-03-29",
    "payment_method": "MOBILE_MONEY",
    "received_by": 3
  }'
```

### 11.6 Update Customer Paid Status via API

```bash
# Update a customer's paid status
curl -X PATCH http://127.0.0.1:8000/api/customers/1/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_access_token>" \
  -d '{
    "paid_status": true
  }'
```

## 12. Testing Access Control

### 12.1 Role-Based Access Testing (as Calling Agent)

1. **Log in as the Calling Agent**

   - Log out of any current account
   - Log in with agent1/dkid9392kd

2. **Verify Limited Access**
   - Try to access Loans directly - should have limited view
   - Try to create a new Loan - should not have permission
   - Try to modify a customer's details - should not have permission
   - Can view and create Interactions - should be permitted
   - Can create Follow-ups - should be permitted

### 12.2 Data Visibility Testing (as Collection Officer)

1. **Log in as the Collection Officer**

   - Log out of the agent account
   - Log in with officer1/dndorl203e

2. **Verify Data Visibility**
   - Should only see assigned customers
   - Should only see loans assigned to you
   - Should be able to create and modify customers
   - Should be able to create loan applications
   - Cannot approve loans (PENDING to ACTIVE)

### 12.3 Approval Authority Testing (as Manager)

1. **Log in as the Manager**

   - Log out of the officer account
   - Log in with manager1/asidol304k3

2. **Verify Manager Capabilities**
   - Can view all officers' customers who report to them (directly or indirectly)
   - Can approve loans (change status from PENDING to ACTIVE)
   - Can restructure loans (change status to RESTRUCTURED)
   - Cannot write off loans (requires Super Manager)

## 13. Reporting and Dashboard

### 13.1 Loan Portfolio Overview

1. **Log in as the Super Manager**

   - Log in with nidhiyashwanth/supernidhi

2. **View Portfolio Statistics** (if implemented)
   - Navigate to Dashboard (if available)
   - Check total loans outstanding
   - Review loan status distribution
   - View payment collection rate

### 13.2 Delinquency Reporting

1. **Identify Delinquent Loans**
   - Filter loans by days_past_due > 0
   - Sort by days_past_due to find most critical cases
   - Check payment_status for categorization

## 14. Swagger API Documentation

1. **Access the API Documentation**
   - Navigate to http://127.0.0.1:8000/api/docs/
   - Log in with nidhiyashwanth/supernidhi
   - Explore available endpoints
   - Test endpoints directly from the Swagger UI

## 15. Troubleshooting Common Issues

### Database Connection Issues

- Verify PostgreSQL is running: `pg_isready -h localhost -p 5432`
- Check database settings in `.env`
- Verify migrations: `python manage.py showmigrations`

### Authentication Issues

- Token expired: request a new token
- Incorrect permissions: verify user role is appropriate for the action
- For the Hierarchy model, when creating relationships, ensure you're selecting from dropdowns rather than trying to enter values directly

### Loan Calculation Issues

- Verify the decimal handling in loan calculations
- Check that principal_amount and interest_rate use Decimal type
- Verify term_months is correctly converted to Decimal when needed

## 16. Clean-up and Reset (for Testing)

```bash
# To reset the database for fresh testing
python manage.py flush  # Will delete all data

# Recreate the superuser after flushing
python manage.py createsuperuser
```

This comprehensive walkthrough should allow you to test all aspects of the RepaySync application, including the role-based access control, loan processing workflow, and all user interactions. Follow the steps in order to experience a complete simulation of the system's functionality.

# Django User Permissions and Groups Setup for RepaySync

Based on the requirements document and problem statement, I'll guide you through setting up appropriate permissions for each user role. The Django admin interface allows us to assign both individual permissions and group-based permissions.

## 1. Create User Groups

Let's first create groups for each role to simplify permission management:

1. **Access Groups in Django Admin**:

   - Go to http://127.0.0.1:8000/admin/
   - Look for "Groups" under the "AUTHENTICATION AND AUTHORIZATION" section
   - Click on "Groups"

2. **Create Super Manager Group**:

   - Click "ADD GROUP +" button
   - Name: `Super Managers`
   - Permissions: Select all available permissions (you can use the search box to filter)
   - Click "Save"

3. **Create Manager Group**:

   - Click "ADD GROUP +" button
   - Name: `Managers`
   - Permissions:
     - Users: Can view user, Can change user (but not delete or add)
     - Customers: Can add, change, view, delete customer
     - Loans: Can add, change, view, delete loan, Can approve loan, Can restructure loan
     - Payments: Can add, change, view, delete payment
     - Interactions: Can add, change, view, delete interaction
     - Follow-ups: Can add, change, view, delete follow-up
     - Hierarchies: Can add, change, view, delete hierarchy
   - Click "Save"

4. **Create Collection Officer Group**:

   - Click "ADD GROUP +" button
   - Name: `Collection Officers`
   - Permissions:
     - Customers: Can add, change, view customer (not delete)
     - Loans: Can add, view, change loan (not delete or approve)
     - Payments: Can add, view, change payment
     - Interactions: Can add, view, change interaction
     - Follow-ups: Can add, view, change follow-up
   - Click "Save"

5. **Create Calling Agent Group**:
   - Click "ADD GROUP +" button
   - Name: `Calling Agents`
   - Permissions:
     - Customers: Can view customer
     - Loans: Can view loan
     - Interactions: Can add, view, change interaction
     - Follow-ups: Can add, view, change follow-up
   - Click "Save"

## 2. Assign Users to Groups

Now, let's assign each user to their appropriate group:

1. **Update the Admin User**:

   - Go to Users list
   - Click on the `admin` user
   - Scroll down to "Groups" section
   - Select "Super Managers"
   - Click "Save"

2. **Update the Manager User**:

   - Go to Users list
   - Click on `manager1`
   - Scroll down to "Groups" section
   - Select "Managers"
   - Click "Save"

3. **Update the Collection Officer**:

   - Go to Users list
   - Click on `officer1`
   - Scroll down to "Groups" section
   - Select "Collection Officers"
   - Click "Save"

4. **Update the Calling Agent**:
   - Go to Users list
   - Click on `agent1`
   - Scroll down to "Groups" section
   - Select "Calling Agents"
   - Click "Save"

## 3. Special Permissions Based on Requirements

There are some special requirements from the problem statement that might require additional permissions:

1. **For Collection Officers**:

   - Only assigned collection officers should be able to update their customers
   - This is likely enforced at the application level through the view logic, not just Django permissions

2. **For Calling Agents**:

   - Can contact any customer (view all customers)
   - Can log updates for any customer (create interactions)

3. **Hierarchy-based Access**:
   - Managers should have access to all customers and interactions of collection officers under them
   - This hierarchy-based permission is implemented through the Hierarchy model and enforced in the views

## 4. Testing the Permissions

After setting up these permissions, you should test each user role:

1. **Log in as Calling Agent**:

   - Should be able to view all customers but not modify them
   - Should be able to create and update interactions
   - Should not be able to create loans or payments

2. **Log in as Collection Officer**:

   - Should only see assigned customers
   - Should be able to create loans (but not approve them)
   - Should be able to record payments
   - Should be able to create and update interactions

3. **Log in as Manager**:

   - Should see all customers assigned to officers under them
   - Should be able to approve loans
   - Should be able to restructure loans

4. **Log in as Super Manager (admin)**:
   - Should have full access to all features
   - Can write off loans
   - Can create and manage all users

This setup aligns with the role-based access control described in the requirements document and problem statement, ensuring each user role has appropriate permissions based on their responsibilities in the system.
