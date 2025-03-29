"""
Tests for the loans app.
"""
from datetime import date, timedelta
from decimal import Decimal
from django.test import TestCase
from django.utils import timezone

from loans.models import Loan, Payment
from customers.models import Customer
from users.models import User


class LoanModelTestCase(TestCase):
    """Test case for the Loan model."""

    def setUp(self):
        """Set up test data."""
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123',
            first_name='Test',
            last_name='User',
            role=User.Role.COLLECTION_OFFICER
        )
        
        # Create a test customer
        self.customer = Customer.objects.create(
            first_name='Jane',
            last_name='Doe',
            primary_phone='+1234567890',
            created_by=self.user
        )
        
        # Create a test loan
        self.loan = Loan.objects.create(
            customer=self.customer,
            loan_reference='LN-1001',
            principal_amount=Decimal('10000.00'),
            interest_rate=Decimal('12.00'),
            term_months=12,
            assigned_officer=self.user,
            created_by=self.user
        )

    def test_loan_creation(self):
        """Test that a loan can be created."""
        self.assertEqual(Loan.objects.count(), 1)
        self.assertEqual(self.loan.loan_reference, 'LN-1001')
        self.assertEqual(self.loan.principal_amount, Decimal('10000.00'))
        self.assertEqual(self.loan.interest_rate, Decimal('12.00'))
        self.assertEqual(self.loan.term_months, 12)
        self.assertEqual(self.loan.status, Loan.Status.PENDING)
        
    def test_loan_total_amount_due(self):
        """Test the total_amount_due property."""
        # For 10000 principal, 12% interest for 1 year: 10000 + (10000 * 0.12 * 1) = 11200
        self.assertEqual(self.loan.total_amount_due, Decimal('11200.00'))
        
    def test_loan_remaining_balance(self):
        """Test the remaining_balance property."""
        # Initially, the remaining balance is the total amount due
        self.assertEqual(self.loan.remaining_balance, self.loan.total_amount_due)
        
        # Add a payment
        Payment.objects.create(
            loan=self.loan,
            payment_reference='PMT-1001',
            amount=Decimal('1000.00'),
            payment_date=date.today(),
            payment_method=Payment.PaymentMethod.CASH,
            received_by=self.user
        )
        
        # Refresh the loan from db
        self.loan.refresh_from_db()
        
        # Now the remaining balance is the total amount due minus the payment
        self.assertEqual(self.loan.remaining_balance, Decimal('10200.00'))
        
    def test_loan_payment_status(self):
        """Test the payment_status property."""
        # Initially, the loan is current
        self.assertEqual(self.loan.payment_status, "Current")
        
        # Set days_past_due to different values and check the status
        self.loan.days_past_due = 20
        self.assertEqual(self.loan.payment_status, "1-30 Days Late")
        
        self.loan.days_past_due = 45
        self.assertEqual(self.loan.payment_status, "31-60 Days Late")
        
        self.loan.days_past_due = 70
        self.assertEqual(self.loan.payment_status, "61-90 Days Late")
        
        self.loan.days_past_due = 100
        self.assertEqual(self.loan.payment_status, "90+ Days Late")
        
        # Mark the loan as paid
        self.loan.status = Loan.Status.PAID
        self.assertEqual(self.loan.payment_status, "Fully Paid")
        
    def test_loan_str_method(self):
        """Test the Loan __str__ method."""
        expected = f"LN-1001 - {self.customer}"
        self.assertEqual(str(self.loan), expected)


class PaymentModelTestCase(TestCase):
    """Test case for the Payment model."""

    def setUp(self):
        """Set up test data."""
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123',
            first_name='Test',
            last_name='User',
            role=User.Role.COLLECTION_OFFICER
        )
        
        # Create a test customer
        self.customer = Customer.objects.create(
            first_name='Jane',
            last_name='Doe',
            primary_phone='+1234567890',
            created_by=self.user
        )
        
        # Create a test loan
        self.loan = Loan.objects.create(
            customer=self.customer,
            loan_reference='LN-1001',
            principal_amount=Decimal('10000.00'),
            interest_rate=Decimal('12.00'),
            term_months=12,
            assigned_officer=self.user,
            created_by=self.user
        )
        
        # Create a test payment
        self.payment = Payment.objects.create(
            loan=self.loan,
            payment_reference='PMT-1001',
            amount=Decimal('1000.00'),
            payment_date=date.today(),
            payment_method=Payment.PaymentMethod.CASH,
            received_by=self.user
        )

    def test_payment_creation(self):
        """Test that a payment can be created."""
        self.assertEqual(Payment.objects.count(), 1)
        self.assertEqual(self.payment.payment_reference, 'PMT-1001')
        self.assertEqual(self.payment.amount, Decimal('1000.00'))
        self.assertEqual(self.payment.payment_method, Payment.PaymentMethod.CASH)
        
    def test_payment_str_method(self):
        """Test the Payment __str__ method."""
        expected = f"PMT-1001 - 1000.00"
        self.assertEqual(str(self.payment), expected)
        
    def test_payment_updates_loan(self):
        """Test that a payment updates the loan."""
        # Refresh the loan from db
        self.loan.refresh_from_db()
        
        # Check that the loan's amount_paid has been updated
        self.assertEqual(self.loan.amount_paid, Decimal('1000.00'))
        
        # Check that the loan's last_payment_date has been set
        self.assertEqual(self.loan.last_payment_date, date.today())
        
        # Create another payment
        Payment.objects.create(
            loan=self.loan,
            payment_reference='PMT-1002',
            amount=Decimal('2000.00'),
            payment_date=date.today() + timedelta(days=1),
            payment_method=Payment.PaymentMethod.BANK_TRANSFER,
            received_by=self.user
        )
        
        # Refresh the loan from db
        self.loan.refresh_from_db()
        
        # Check that the loan's amount_paid has been updated
        self.assertEqual(self.loan.amount_paid, Decimal('3000.00'))
        
        # Check that the loan's last_payment_date has been updated to the more recent payment
        self.assertEqual(self.loan.last_payment_date, date.today() + timedelta(days=1))
        
    def test_payment_pays_off_loan(self):
        """Test that a payment that pays off the loan updates the loan status."""
        # Create a payment that pays off the loan
        Payment.objects.create(
            loan=self.loan,
            payment_reference='PMT-1002',
            amount=Decimal('10200.00'),  # This will pay off the loan
            payment_date=date.today(),
            payment_method=Payment.PaymentMethod.BANK_TRANSFER,
            received_by=self.user
        )
        
        # Refresh the loan from db
        self.loan.refresh_from_db()
        
        # Check that the loan's status has been updated to paid
        self.assertEqual(self.loan.status, Loan.Status.PAID) 