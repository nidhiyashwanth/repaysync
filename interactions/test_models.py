"""
Tests for the interactions app.
"""
from datetime import date, datetime, timedelta
from django.test import TestCase
from django.utils import timezone

from interactions.models import Interaction, FollowUp
from customers.models import Customer
from loans.models import Loan
from users.models import User
from decimal import Decimal


class InteractionModelTestCase(TestCase):
    """Test case for the Interaction model."""

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
        
        # Create a test interaction
        self.start_time = timezone.now()
        self.interaction = Interaction.objects.create(
            customer=self.customer,
            loan=self.loan,
            interaction_type=Interaction.InteractionType.CALL,
            initiated_by=self.user,
            start_time=self.start_time,
            contact_number='+1234567890',
            notes="Test call to customer about upcoming payment"
        )

    def test_interaction_creation(self):
        """Test that an interaction can be created."""
        self.assertEqual(Interaction.objects.count(), 1)
        self.assertEqual(self.interaction.customer, self.customer)
        self.assertEqual(self.interaction.loan, self.loan)
        self.assertEqual(self.interaction.interaction_type, Interaction.InteractionType.CALL)
        self.assertEqual(self.interaction.initiated_by, self.user)
        self.assertEqual(self.interaction.start_time, self.start_time)
        self.assertEqual(self.interaction.notes, "Test call to customer about upcoming payment")
        
    def test_interaction_str_method(self):
        """Test the Interaction __str__ method."""
        expected = f"Phone Call with {self.customer} on {self.start_time.strftime('%Y-%m-%d %H:%M')}"
        self.assertEqual(str(self.interaction), expected)
        
    def test_interaction_with_outcome(self):
        """Test interaction with an outcome."""
        self.interaction.outcome = Interaction.InteractionOutcome.PAYMENT_PROMISED
        self.interaction.payment_promise_amount = Decimal('1000.00')
        self.interaction.payment_promise_date = date.today() + timedelta(days=3)
        self.interaction.save()
        
        updated_interaction = Interaction.objects.get(id=self.interaction.id)
        self.assertEqual(updated_interaction.outcome, Interaction.InteractionOutcome.PAYMENT_PROMISED)
        self.assertEqual(updated_interaction.payment_promise_amount, Decimal('1000.00'))
        self.assertEqual(updated_interaction.payment_promise_date, date.today() + timedelta(days=3))
        
    def test_interaction_duration_calculation(self):
        """Test interaction duration calculation."""
        # Set end_time 5 minutes after start_time
        end_time = self.start_time + timedelta(minutes=5)
        self.interaction.end_time = end_time
        self.interaction.save()
        
        # Refresh from db
        self.interaction.refresh_from_db()
        
        # Should be 5 minutes = 300 seconds
        self.assertEqual(self.interaction.duration, 300)
        
    def test_interaction_without_loan(self):
        """Test interaction without a linked loan."""
        interaction = Interaction.objects.create(
            customer=self.customer,
            interaction_type=Interaction.InteractionType.EMAIL,
            initiated_by=self.user,
            start_time=timezone.now(),
            notes="General follow up email"
        )
        self.assertIsNone(interaction.loan)
        self.assertEqual(interaction.customer, self.customer)


class FollowUpModelTestCase(TestCase):
    """Test case for the FollowUp model."""

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
        
        # Create another test user for assignments
        self.another_user = User.objects.create_user(
            username='anotheruser',
            email='another@example.com',
            password='password456',
            first_name='Another',
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
        
        # Create a test interaction
        self.interaction = Interaction.objects.create(
            customer=self.customer,
            interaction_type=Interaction.InteractionType.CALL,
            initiated_by=self.user,
            start_time=timezone.now(),
            notes="Test call to customer about upcoming payment"
        )
        
        # Create a test follow-up
        self.scheduled_date = date.today() + timedelta(days=7)
        self.follow_up = FollowUp.objects.create(
            interaction=self.interaction,
            customer=self.customer,
            follow_up_type=FollowUp.FollowUpType.CALL,
            scheduled_date=self.scheduled_date,
            assigned_to=self.user,
            priority=FollowUp.FollowUpStatus.PENDING,
            notes="Follow up on payment promise",
            created_by=self.user
        )

    def test_follow_up_creation(self):
        """Test that a follow-up can be created."""
        self.assertEqual(FollowUp.objects.count(), 1)
        self.assertEqual(self.follow_up.interaction, self.interaction)
        self.assertEqual(self.follow_up.customer, self.customer)
        self.assertEqual(self.follow_up.follow_up_type, FollowUp.FollowUpType.CALL)
        self.assertEqual(self.follow_up.scheduled_date, self.scheduled_date)
        self.assertEqual(self.follow_up.assigned_to, self.user)
        self.assertEqual(self.follow_up.status, FollowUp.FollowUpStatus.PENDING)
        self.assertEqual(self.follow_up.notes, "Follow up on payment promise")
        
    def test_follow_up_str_method(self):
        """Test the FollowUp __str__ method."""
        expected = f"Phone Call with {self.customer} on {self.scheduled_date}"
        self.assertEqual(str(self.follow_up), expected)
        
    def test_follow_up_completion(self):
        """Test completing a follow-up."""
        complete_time = timezone.now()
        self.follow_up.status = FollowUp.FollowUpStatus.COMPLETED
        self.follow_up.result = "Customer made payment as promised"
        self.follow_up.completed_at = complete_time
        self.follow_up.completed_by = self.user
        self.follow_up.save()
        
        updated_follow_up = FollowUp.objects.get(id=self.follow_up.id)
        self.assertEqual(updated_follow_up.status, FollowUp.FollowUpStatus.COMPLETED)
        self.assertEqual(updated_follow_up.result, "Customer made payment as promised")
        self.assertEqual(updated_follow_up.completed_at, complete_time)
        self.assertEqual(updated_follow_up.completed_by, self.user)
        
    def test_follow_up_reassignment(self):
        """Test reassigning a follow-up to another user."""
        self.follow_up.assigned_to = self.another_user
        self.follow_up.save()
        
        updated_follow_up = FollowUp.objects.get(id=self.follow_up.id)
        self.assertEqual(updated_follow_up.assigned_to, self.another_user)
        
    def test_follow_up_rescheduling(self):
        """Test rescheduling a follow-up."""
        new_date = date.today() + timedelta(days=14)
        self.follow_up.status = FollowUp.FollowUpStatus.RESCHEDULED
        self.follow_up.scheduled_date = new_date
        self.follow_up.save()
        
        updated_follow_up = FollowUp.objects.get(id=self.follow_up.id)
        self.assertEqual(updated_follow_up.status, FollowUp.FollowUpStatus.RESCHEDULED)
        self.assertEqual(updated_follow_up.scheduled_date, new_date)
