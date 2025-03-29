"""
Tests for the API endpoints.
"""
from django.urls import reverse
from django.utils import timezone
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from decimal import Decimal
from datetime import date, timedelta

from users.models import User
from customers.models import Customer
from loans.models import Loan, Payment
from interactions.models import Interaction, FollowUp

# Override the default DRF settings for testing
TEST_DRF_SETTINGS = {
    'DEFAULT_AUTHENTICATION_CLASSES': [],
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.AllowAny'],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

@override_settings(REST_FRAMEWORK=TEST_DRF_SETTINGS)
class CustomerAPITestCase(APITestCase):
    """Test case for the Customer API endpoints."""

    def setUp(self):
        """Set up test data."""
        # Create a superuser for auth
        self.superuser = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpassword',
            first_name='Admin',
            last_name='User'
        )
        
        # Create a regular user for testing permissions
        self.regular_user = User.objects.create_user(
            username='regular',
            email='regular@example.com',
            password='regularpassword',
            first_name='Regular',
            last_name='User',
            role=User.Role.COLLECTION_OFFICER
        )
        
        # Create test customers
        self.customer1 = Customer.objects.create(
            first_name='Jane',
            last_name='Doe',
            gender=Customer.Gender.FEMALE,
            primary_phone='+1234567890',
            email='jane.doe@example.com',
            city='Test City',
            created_by=self.superuser
        )
        
        self.customer2 = Customer.objects.create(
            first_name='John',
            last_name='Smith',
            gender=Customer.Gender.MALE,
            primary_phone='+0987654321',
            email='john.smith@example.com',
            city='Another City',
            created_by=self.superuser
        )
        
        # Set up API client and authenticate as superuser
        self.client = APIClient()
        self.client.force_authenticate(user=self.superuser)

    def test_get_customers_list(self):
        """Test retrieving the list of customers."""
        url = reverse('customer-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        
    def test_get_customer_detail(self):
        """Test retrieving a single customer."""
        url = reverse('customer-detail', kwargs={'pk': self.customer1.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Jane')
        self.assertEqual(response.data['last_name'], 'Doe')
        self.assertEqual(response.data['primary_phone'], '+1234567890')
        
    def test_create_customer(self):
        """Test creating a new customer."""
        url = reverse('customer-list')
        data = {
            'first_name': 'New',
            'last_name': 'Customer',
            'gender': Customer.Gender.MALE,
            'primary_phone': '+1122334455',
            'email': 'new.customer@example.com',
            'city': 'New City'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Customer.objects.count(), 3)
        self.assertEqual(Customer.objects.get(email='new.customer@example.com').first_name, 'New')
        
    def test_update_customer(self):
        """Test updating a customer."""
        url = reverse('customer-detail', kwargs={'pk': self.customer1.pk})
        data = {
            'first_name': 'Jane',
            'last_name': 'Doe',
            'gender': Customer.Gender.FEMALE,
            'primary_phone': '+1234567890',
            'email': 'jane.doe@example.com',
            'city': 'Updated City'  # Changed city
        }
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['city'], 'Updated City')
        
        # Verify the update in the database
        self.customer1.refresh_from_db()
        self.assertEqual(self.customer1.city, 'Updated City')
        
    def test_partial_update_customer(self):
        """Test partially updating a customer."""
        url = reverse('customer-detail', kwargs={'pk': self.customer1.pk})
        data = {
            'notes': 'New notes added'  # Only updating the notes field
        }
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['notes'], 'New notes added')
        
        # Verify the update in the database
        self.customer1.refresh_from_db()
        self.assertEqual(self.customer1.notes, 'New notes added')
        
    def test_delete_customer(self):
        """Test deleting a customer."""
        url = reverse('customer-detail', kwargs={'pk': self.customer1.pk})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Customer.objects.count(), 1)
        
    def test_search_customers(self):
        """Test searching for customers."""
        url = reverse('customer-list') + '?search=Jane'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['first_name'], 'Jane')
        
    def test_filter_customers_by_city(self):
        """Test filtering customers by city."""
        url = reverse('customer-list') + '?city=Test City'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['city'], 'Test City')


@override_settings(REST_FRAMEWORK=TEST_DRF_SETTINGS)
class LoanAPITestCase(APITestCase):
    """Test case for the Loan API endpoints."""

    def setUp(self):
        """Set up test data."""
        # Create a superuser for auth
        self.superuser = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpassword',
            first_name='Admin',
            last_name='User'
        )
        
        # Create test customers
        self.customer = Customer.objects.create(
            first_name='Jane',
            last_name='Doe',
            gender=Customer.Gender.FEMALE,
            primary_phone='+1234567890',
            email='jane.doe@example.com',
            created_by=self.superuser
        )
        
        # Create test loans
        self.loan1 = Loan.objects.create(
            customer=self.customer,
            loan_reference='LN-1001',
            principal_amount=Decimal('10000.00'),
            interest_rate=Decimal('12.00'),
            term_months=12,
            assigned_officer=self.superuser,
            created_by=self.superuser
        )
        
        self.loan2 = Loan.objects.create(
            customer=self.customer,
            loan_reference='LN-1002',
            principal_amount=Decimal('5000.00'),
            interest_rate=Decimal('10.00'),
            term_months=6,
            status=Loan.Status.ACTIVE,
            assigned_officer=self.superuser,
            created_by=self.superuser
        )
        
        # Set up API client and authenticate as superuser
        self.client = APIClient()
        self.client.force_authenticate(user=self.superuser)

    def test_get_loans_list(self):
        """Test retrieving the list of loans."""
        url = reverse('loan-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        
    def test_get_loan_detail(self):
        """Test retrieving a single loan."""
        url = reverse('loan-detail', kwargs={'pk': self.loan1.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['loan_reference'], 'LN-1001')
        self.assertEqual(response.data['principal_amount'], '10000.00')
        self.assertEqual(response.data['term_months'], 12)
        
    def test_create_loan(self):
        """Test creating a new loan."""
        url = reverse('loan-list')
        data = {
            'customer': self.customer.id,
            'loan_reference': 'LN-1003',
            'principal_amount': '15000.00',
            'interest_rate': '11.00',
            'term_months': 24,
            'assigned_officer': self.superuser.id
        }
        response = self.client.post(url, data, format='json')
        
        print(f"Response status: {response.status_code}")
        print(f"Response data: {response.data}")
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Get loan reference from response
        created_loan_reference = response.data['loan_reference']
        
        # Verify loan was created
        loan = Loan.objects.get(loan_reference=created_loan_reference)
        self.assertEqual(loan.principal_amount, Decimal('15000.00'))
        self.assertEqual(loan.term_months, 24)
        
    def test_update_loan(self):
        """Test updating a loan."""
        url = reverse('loan-detail', kwargs={'pk': self.loan1.pk})
        data = {
            'customer': self.customer.id,
            'loan_reference': 'LN-1001',
            'principal_amount': '12000.00',  # Changed amount
            'interest_rate': '12.00',
            'term_months': 12,
            'assigned_officer': self.superuser.id
        }
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['principal_amount'], '12000.00')
        
        # Verify the update in the database
        self.loan1.refresh_from_db()
        self.assertEqual(self.loan1.principal_amount, Decimal('12000.00'))
        
    def test_filter_loans_by_status(self):
        """Test filtering loans by status."""
        url = reverse('loan-list') + '?status=ACTIVE'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['status'], 'ACTIVE')


@override_settings(REST_FRAMEWORK=TEST_DRF_SETTINGS)
class InteractionAPITestCase(APITestCase):
    """Test case for the Interaction API endpoints."""

    def setUp(self):
        """Set up test data."""
        # Create a superuser for auth
        self.superuser = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpassword',
            first_name='Admin',
            last_name='User'
        )
        
        # Create test customer
        self.customer = Customer.objects.create(
            first_name='Jane',
            last_name='Doe',
            gender=Customer.Gender.FEMALE,
            primary_phone='+1234567890',
            email='jane.doe@example.com',
            created_by=self.superuser
        )
        
        # Create test loan
        self.loan = Loan.objects.create(
            customer=self.customer,
            loan_reference='LN-1001',
            principal_amount=Decimal('10000.00'),
            interest_rate=Decimal('12.00'),
            term_months=12,
            assigned_officer=self.superuser,
            created_by=self.superuser
        )
        
        # Create test interactions
        self.interaction1 = Interaction.objects.create(
            customer=self.customer,
            loan=self.loan,
            interaction_type=Interaction.InteractionType.CALL,
            initiated_by=self.superuser,
            start_time=timezone.now(),
            contact_number='+1234567890',
            notes="First call to customer"
        )
        
        self.interaction2 = Interaction.objects.create(
            customer=self.customer,
            interaction_type=Interaction.InteractionType.EMAIL,
            initiated_by=self.superuser,
            start_time=timezone.now() - timedelta(days=1),  # Yesterday
            notes="Email to customer"
        )
        
        # Set up API client and authenticate as superuser
        self.client = APIClient()
        self.client.force_authenticate(user=self.superuser)

    def test_get_interactions_list(self):
        """Test retrieving the list of interactions."""
        url = reverse('interaction-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        
    def test_get_interaction_detail(self):
        """Test retrieving a single interaction."""
        url = reverse('interaction-detail', kwargs={'pk': self.interaction1.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['interaction_type'], 'CALL')
        self.assertEqual(response.data['notes'], 'First call to customer')
        
    def test_create_interaction(self):
        """Test creating a new interaction."""
        url = reverse('interaction-list')
        data = {
            'customer': self.customer.id,
            'interaction_type': Interaction.InteractionType.MEETING,
            'initiated_by': self.superuser.id,
            'start_time': timezone.now().isoformat(),
            'notes': 'In-person meeting with customer'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Interaction.objects.count(), 3)
        self.assertEqual(Interaction.objects.latest('id').notes, 'In-person meeting with customer')
        
    def test_filter_interactions_by_type(self):
        """Test filtering interactions by type."""
        url = reverse('interaction-list') + '?interaction_type=CALL'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['interaction_type'], 'CALL')
        
    def test_filter_interactions_by_customer(self):
        """Test filtering interactions by customer."""
        url = reverse('interaction-list') + f'?customer={self.customer.id}'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)  # Both interactions are for the same customer 