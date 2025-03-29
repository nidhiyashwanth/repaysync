"""
Tests for the customers app.
"""
from django.test import TestCase
from django.core.exceptions import ValidationError
from decimal import Decimal

from customers.models import Customer
from users.models import User


class CustomerModelTestCase(TestCase):
    """Test case for the Customer model."""

    def setUp(self):
        """Set up test data."""
        # Create a test user for assignments
        self.collection_officer = User.objects.create_user(
            username='officer1',
            email='officer1@example.com',
            password='password123',
            first_name='John',
            last_name='Officer',
            role=User.Role.COLLECTION_OFFICER
        )
        
        # Create a test customer
        self.customer = Customer.objects.create(
            first_name='Jane',
            last_name='Doe',
            gender=Customer.Gender.FEMALE,
            primary_phone='+1234567890',
            email='jane.doe@example.com',
            city='Test City',
            assigned_officer=self.collection_officer,
            created_by=self.collection_officer
        )

    def test_customer_creation(self):
        """Test that a customer can be created with the minimum required fields."""
        customer_count = Customer.objects.count()
        self.assertEqual(customer_count, 1)
        self.assertEqual(self.customer.first_name, 'Jane')
        self.assertEqual(self.customer.last_name, 'Doe')
        self.assertEqual(self.customer.gender, Customer.Gender.FEMALE)
        self.assertEqual(self.customer.primary_phone, '+1234567890')
        self.assertEqual(self.customer.email, 'jane.doe@example.com')
        self.assertEqual(self.customer.city, 'Test City')
        self.assertEqual(self.customer.assigned_officer, self.collection_officer)
        self.assertEqual(self.customer.created_by, self.collection_officer)
        
    def test_customer_str_method(self):
        """Test the Customer __str__ method."""
        self.assertEqual(str(self.customer), 'Jane Doe')
        
    def test_customer_full_name_property(self):
        """Test the Customer full_name property."""
        self.assertEqual(self.customer.full_name, 'Jane Doe')
        
    def test_customer_with_empty_optional_fields(self):
        """Test creating a customer with minimum required fields."""
        new_customer = Customer.objects.create(
            first_name='John',
            last_name='Smith',
            primary_phone='+9876543210'
        )
        self.assertEqual(new_customer.first_name, 'John')
        self.assertEqual(new_customer.last_name, 'Smith')
        self.assertEqual(new_customer.primary_phone, '+9876543210')
        self.assertEqual(new_customer.email, '')
        self.assertIsNone(new_customer.assigned_officer)
        self.assertIsNone(new_customer.created_by)
        
    def test_customer_with_monthly_income(self):
        """Test customer with monthly income."""
        self.customer.monthly_income = Decimal('5000.00')
        self.customer.save()
        saved_customer = Customer.objects.get(id=self.customer.id)
        self.assertEqual(saved_customer.monthly_income, Decimal('5000.00'))

    def test_customer_default_is_active(self):
        """Test that a customer is active by default."""
        self.assertTrue(self.customer.is_active)

    def test_customer_ordering(self):
        """Test that customers are ordered by last_name, first_name."""
        # Create customers with different names
        Customer.objects.create(
            first_name='Alice',
            last_name='Smith',
            primary_phone='+1111111111'
        )
        Customer.objects.create(
            first_name='Bob',
            last_name='Adams',
            primary_phone='+2222222222'
        )
        
        # Get customers ordered as per Meta.ordering
        customers = Customer.objects.all()
        self.assertEqual(customers[0].last_name, 'Adams')  # Adams comes first alphabetically
        self.assertEqual(customers[1].last_name, 'Doe')     # Doe is second
        self.assertEqual(customers[2].last_name, 'Smith')  # Smith is last
