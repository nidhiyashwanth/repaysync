import os
import django
import datetime

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "repaysync.settings")
django.setup()

from django.contrib.auth import get_user_model
from customers.models import Customer
from loans.models import Loan, Payment
from interactions.models import Interaction, FollowUp
from users.models import Hierarchy

User = get_user_model()

# Create test users
def create_test_users():
    print("Creating test users...")
    # Manager
    manager, created = User.objects.get_or_create(
        username='manager1',
        defaults={
            'email': 'manager1@repaysync.com',
            'first_name': 'John',
            'last_name': 'Manager',
            'role': 'MANAGER',
            'phone': '+1234567890',
            'is_staff': True,
            'is_active': True,
        }
    )
    if created:
        manager.set_password('asidol304k3')
        manager.save()
        print(f"Manager user '{manager.username}' created.")
    else:
        print(f"Manager user '{manager.username}' already exists.")

    # Collection Officer
    officer, created = User.objects.get_or_create(
        username='officer1',
        defaults={
            'email': 'officer1@repaysync.com',
            'first_name': 'Sarah',
            'last_name': 'Officer',
            'role': 'COLLECTION_OFFICER',
            'phone': '+1234567891',
            'is_staff': True,
            'is_active': True,
        }
    )
    if created:
        officer.set_password('dndorl203e')
        officer.save()
        print(f"Collection Officer '{officer.username}' created.")
    else:
        print(f"Collection Officer '{officer.username}' already exists.")

    # Calling Agent
    agent, created = User.objects.get_or_create(
        username='agent1',
        defaults={
            'email': 'agent1@repaysync.com',
            'first_name': 'Alex',
            'last_name': 'Agent',
            'role': 'CALLING_AGENT',
            'phone': '+1234567892',
            'is_staff': True,
            'is_active': True,
        }
    )
    if created:
        agent.set_password('dkid9392kd')
        agent.save()
        print(f"Calling Agent '{agent.username}' created.")
    else:
        print(f"Calling Agent '{agent.username}' already exists.")
    
    # Create hierarchy relationship
    hierarchy, created = Hierarchy.objects.get_or_create(
        manager=manager,
        collection_officer=officer,
        defaults={
            'created_at': datetime.datetime.now(),
            'updated_at': datetime.datetime.now(),
        }
    )
    if created:
        print(f"Hierarchy relationship created between {manager.username} and {officer.username}.")
    else:
        print(f"Hierarchy relationship already exists.")
    
    return manager, officer, agent

# Create test customers
def create_test_customers(officer):
    print("Creating test customers...")
    # Customer 1
    customer1, created = Customer.objects.get_or_create(
        primary_phone='+1987654321',
        defaults={
            'first_name': 'Michael',
            'last_name': 'Brown',
            'gender': 'MALE',
            'date_of_birth': datetime.date(1987, 7, 24),
            'national_id': '2930494294903',
            'email': 'michael.brown@example.com',
            'city': 'San Francisco',
            'state': 'CA',
            'country': 'US',
            'branch': 'North Branch',
            'paid_status': False,
            'monthly_income': 5000.00,
            'assigned_officer': officer,
            'notes': 'New customer with good credit history',
        }
    )
    if created:
        print(f"Customer {customer1.first_name} {customer1.last_name} created.")
    else:
        print(f"Customer {customer1.first_name} {customer1.last_name} already exists.")
    
    # Customer 2
    customer2, created = Customer.objects.get_or_create(
        primary_phone='+1987654322',
        defaults={
            'first_name': 'Emma',
            'last_name': 'Wilson',
            'gender': 'FEMALE',
            'date_of_birth': datetime.date(1995, 9, 3),
            'national_id': '39474948392',
            'email': 'emma.wilson@example.com',
            'city': 'Los Angeles',
            'state': 'CA',
            'country': 'US',
            'branch': 'South Branch',
            'paid_status': False,
            'monthly_income': 4500.00,
            'assigned_officer': officer,
            'notes': 'New customer referred by Michael Brown',
        }
    )
    if created:
        print(f"Customer {customer2.first_name} {customer2.last_name} created.")
    else:
        print(f"Customer {customer2.first_name} {customer2.last_name} already exists.")
    
    return customer1, customer2

# Create test loans
def create_test_loans(customers, officer, manager):
    print("Creating test loans...")
    customer1, customer2 = customers
    today = datetime.date.today()
    
    # Loan for Customer 1
    loan1, created = Loan.objects.get_or_create(
        customer=customer1,
        principal_amount=10000.00,
        defaults={
            'status': 'PENDING',
            'interest_rate': 12.00,
            'term_months': 12,
            'payment_frequency': 'MONTHLY',
            'assigned_officer': officer,
            'notes': 'Home renovation loan',
        }
    )
    if created:
        print(f"Loan for {customer1.first_name} {customer1.last_name} created.")
    else:
        print(f"Loan for {customer1.first_name} {customer1.last_name} already exists.")
    
    # Approve loan for Customer 1
    if loan1.status == 'PENDING':
        loan1.status = 'ACTIVE'
        loan1.approved_by = manager
        loan1.approval_date = today
        loan1.disbursement_date = today
        loan1.first_payment_date = today + datetime.timedelta(days=30)
        loan1.maturity_date = today + datetime.timedelta(days=365)
        loan1.save()
        print(f"Loan for {customer1.first_name} {customer1.last_name} approved.")
    
    # Loan for Customer 2
    loan2, created = Loan.objects.get_or_create(
        customer=customer2,
        principal_amount=5000.00,
        defaults={
            'status': 'PENDING',
            'interest_rate': 10.00,
            'term_months': 6,
            'payment_frequency': 'MONTHLY',
            'assigned_officer': officer,
            'notes': 'Personal loan for education',
        }
    )
    if created:
        print(f"Loan for {customer2.first_name} {customer2.last_name} created.")
    else:
        print(f"Loan for {customer2.first_name} {customer2.last_name} already exists.")
    
    # Approve loan for Customer 2
    if loan2.status == 'PENDING':
        loan2.status = 'ACTIVE'
        loan2.approved_by = manager
        loan2.approval_date = today
        loan2.disbursement_date = today
        loan2.first_payment_date = today + datetime.timedelta(days=30)
        loan2.maturity_date = today + datetime.timedelta(days=180)
        loan2.save()
        print(f"Loan for {customer2.first_name} {customer2.last_name} approved.")
    
    return loan1, loan2

# Create test payments
def create_test_payments(loan, officer):
    print("Recording payments...")
    today = datetime.date.today()
    
    # First payment
    payment1, created = Payment.objects.get_or_create(
        loan=loan,
        amount=1000.00,
        payment_date=today,
        defaults={
            'payment_method': 'CASH',
            'received_by': officer,
            'notes': 'First payment received',
        }
    )
    if created:
        print(f"First payment of ${payment1.amount} recorded.")
    else:
        print(f"Payment already exists.")
    
    # Second payment
    payment2, created = Payment.objects.get_or_create(
        loan=loan,
        amount=1000.00,
        payment_date=today,
        payment_method='BANK_TRANSFER',
        defaults={
            'received_by': officer,
            'notes': 'Second payment received',
        }
    )
    if created:
        print(f"Second payment of ${payment2.amount} recorded.")
    else:
        print(f"Payment already exists.")
    
    # Update customer paid status
    customer = loan.customer
    customer.paid_status = True
    customer.save()
    print(f"Updated paid status for {customer.first_name} {customer.last_name}.")
    
    return payment1, payment2

# Create test interactions and follow-ups
def create_test_interactions(customer, loan, agent, officer):
    print("Recording interactions and follow-ups...")
    now = datetime.datetime.now()
    
    # Record interaction
    interaction, created = Interaction.objects.get_or_create(
        customer=customer,
        loan=loan,
        start_time=now - datetime.timedelta(minutes=15),
        defaults={
            'interaction_type': 'CALL',
            'end_time': now,
            'contact_person': f"{customer.first_name} {customer.last_name}",
            'outcome': 'SUCCESSFUL',
            'notes': 'Called to remind about upcoming payment. Customer confirmed payment will be made next week.',
            'initiated_by': agent,
        }
    )
    if created:
        print(f"Interaction recorded for {customer.first_name} {customer.last_name}.")
    else:
        print(f"Interaction already exists.")
    
    # Create follow-up
    next_week = datetime.date.today() + datetime.timedelta(days=7)
    follow_up, created = FollowUp.objects.get_or_create(
        related_interaction=interaction,
        customer=customer,
        scheduled_date=next_week,
        scheduled_time=datetime.time(10, 0),
        defaults={
            'description': 'Follow up on payment promise',
            'priority': 'MEDIUM',
            'assigned_to': officer,
            'status': 'PENDING',
        }
    )
    if created:
        print(f"Follow-up scheduled for {next_week}.")
    else:
        print(f"Follow-up already exists.")
    
    # Complete follow-up
    if follow_up.status == 'PENDING':
        follow_up.status = 'COMPLETED'
        follow_up.completion_date = datetime.date.today()
        follow_up.completion_time = datetime.datetime.now().time()
        follow_up.result = 'Payment received as promised'
        follow_up.save()
        print(f"Follow-up marked as completed.")
    
    return interaction, follow_up

# Run test flow
def run_test_flow():
    print("Starting RepaySync test flow...")
    
    # Create users
    manager, officer, agent = create_test_users()
    
    # Create customers
    customers = create_test_customers(officer)
    
    # Create loans
    loans = create_test_loans(customers, officer, manager)
    
    # Record payments for the first loan
    payments = create_test_payments(loans[0], officer)
    
    # Record interactions and follow-ups
    interaction, follow_up = create_test_interactions(customers[0], loans[0], agent, officer)
    
    print("\nTest flow completed successfully!")
    print(f"You can now log in with any of these accounts:")
    print(f"Superuser: nidhiyashwanth / supernidhi")
    print(f"Manager: manager1 / asidol304k3")
    print(f"Collection Officer: officer1 / dndorl203e")
    print(f"Calling Agent: agent1 / dkid9392kd")
    print("\nOpen http://localhost:8000/admin/ in your browser to access the admin interface.")

if __name__ == "__main__":
    run_test_flow() 