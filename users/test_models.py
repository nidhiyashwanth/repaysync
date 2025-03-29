"""
Tests for the users app.
"""
from django.test import TestCase
from django.core.exceptions import ValidationError

from users.models import User, Hierarchy


class UserModelTestCase(TestCase):
    """Test case for the User model."""

    def setUp(self):
        """Set up test data."""
        # Create different users with different roles
        self.super_manager = User.objects.create_user(
            username='supermanager',
            email='supermanager@example.com',
            password='password123',
            first_name='Super',
            last_name='Manager',
            role=User.Role.SUPER_MANAGER
        )
        
        self.manager = User.objects.create_user(
            username='manager',
            email='manager@example.com',
            password='password123',
            first_name='Regular',
            last_name='Manager',
            role=User.Role.MANAGER
        )
        
        self.collection_officer = User.objects.create_user(
            username='officer',
            email='officer@example.com',
            password='password123',
            first_name='Collection',
            last_name='Officer',
            role=User.Role.COLLECTION_OFFICER
        )
        
        self.calling_agent = User.objects.create_user(
            username='agent',
            email='agent@example.com',
            password='password123',
            first_name='Calling',
            last_name='Agent',
            role=User.Role.CALLING_AGENT,
            phone='+1234567890'
        )

    def test_user_creation(self):
        """Test that users can be created with different roles."""
        self.assertEqual(User.objects.count(), 4)
        self.assertEqual(self.super_manager.role, User.Role.SUPER_MANAGER)
        self.assertEqual(self.manager.role, User.Role.MANAGER)
        self.assertEqual(self.collection_officer.role, User.Role.COLLECTION_OFFICER)
        self.assertEqual(self.calling_agent.role, User.Role.CALLING_AGENT)
        
    def test_user_str_method(self):
        """Test the User __str__ method."""
        expected = f"Regular Manager (Manager)"
        self.assertEqual(str(self.manager), expected)
        
    def test_user_phone_field(self):
        """Test user phone field."""
        self.assertEqual(self.calling_agent.phone, '+1234567890')
        
    def test_user_role_properties(self):
        """Test role property methods."""
        self.assertTrue(self.super_manager.is_super_manager)
        self.assertTrue(self.manager.is_manager)
        self.assertTrue(self.collection_officer.is_collection_officer)
        self.assertTrue(self.calling_agent.is_calling_agent)
        
        self.assertFalse(self.manager.is_super_manager)
        self.assertFalse(self.collection_officer.is_manager)
        self.assertFalse(self.calling_agent.is_collection_officer)
        self.assertFalse(self.super_manager.is_calling_agent)
        
    def test_user_created_at_field(self):
        """Test that created_at field is automatically set."""
        self.assertIsNotNone(self.super_manager.created_at)
        self.assertIsNotNone(self.manager.created_at)
        self.assertIsNotNone(self.collection_officer.created_at)
        self.assertIsNotNone(self.calling_agent.created_at)
        
    def test_user_updated_at_field(self):
        """Test that updated_at field is automatically set."""
        self.assertIsNotNone(self.super_manager.updated_at)
        
        # Test that updated_at changes on save
        initial_updated_at = self.super_manager.updated_at
        self.super_manager.first_name = "Updated"
        self.super_manager.save()
        self.super_manager.refresh_from_db()
        self.assertNotEqual(self.super_manager.updated_at, initial_updated_at)
        

class HierarchyModelTestCase(TestCase):
    """Test case for the Hierarchy model."""

    def setUp(self):
        """Set up test data."""
        # Create users with different roles
        self.super_manager = User.objects.create_user(
            username='supermanager',
            email='supermanager@example.com',
            password='password123',
            first_name='Super',
            last_name='Manager',
            role=User.Role.SUPER_MANAGER
        )
        
        self.manager = User.objects.create_user(
            username='manager',
            email='manager@example.com',
            password='password123',
            first_name='Regular',
            last_name='Manager',
            role=User.Role.MANAGER
        )
        
        self.collection_officer1 = User.objects.create_user(
            username='officer1',
            email='officer1@example.com',
            password='password123',
            first_name='Collection',
            last_name='Officer1',
            role=User.Role.COLLECTION_OFFICER
        )
        
        self.collection_officer2 = User.objects.create_user(
            username='officer2',
            email='officer2@example.com',
            password='password123',
            first_name='Collection',
            last_name='Officer2',
            role=User.Role.COLLECTION_OFFICER
        )
        
        self.calling_agent = User.objects.create_user(
            username='agent',
            email='agent@example.com',
            password='password123',
            first_name='Calling',
            last_name='Agent',
            role=User.Role.CALLING_AGENT
        )
        
        # Create hierarchies
        self.hierarchy1 = Hierarchy.objects.create(
            manager=self.super_manager,
            collection_officer=self.collection_officer1
        )
        
        self.hierarchy2 = Hierarchy.objects.create(
            manager=self.manager,
            collection_officer=self.collection_officer2
        )

    def test_hierarchy_creation(self):
        """Test that hierarchies can be created."""
        self.assertEqual(Hierarchy.objects.count(), 2)
        self.assertEqual(self.hierarchy1.manager, self.super_manager)
        self.assertEqual(self.hierarchy1.collection_officer, self.collection_officer1)
        self.assertEqual(self.hierarchy2.manager, self.manager)
        self.assertEqual(self.hierarchy2.collection_officer, self.collection_officer2)
        
    def test_hierarchy_str_method(self):
        """Test the Hierarchy __str__ method."""
        expected = f"{self.collection_officer1} reports to {self.super_manager}"
        self.assertEqual(str(self.hierarchy1), expected)
        
    def test_hierarchy_unique_together_constraint(self):
        """Test that a collection officer can't be assigned to the same manager twice."""
        # Attempt to create a duplicate hierarchy
        with self.assertRaises(Exception):
            Hierarchy.objects.create(
                manager=self.super_manager,
                collection_officer=self.collection_officer1
            )
            
    def test_hierarchy_clean_method(self):
        """Test the clean method validation."""
        # Test validation against a user being their own manager
        hierarchy = Hierarchy(
            manager=self.manager,
            collection_officer=self.manager
        )
        with self.assertRaises(ValidationError):
            hierarchy.clean()
            
        # Test validation against a non-manager in manager role
        hierarchy = Hierarchy(
            manager=self.calling_agent,
            collection_officer=self.collection_officer1
        )
        with self.assertRaises(ValidationError):
            hierarchy.clean()
            
        # Test validation against a non-collection officer in collection_officer role
        hierarchy = Hierarchy(
            manager=self.manager,
            collection_officer=self.calling_agent
        )
        with self.assertRaises(ValidationError):
            hierarchy.clean()
    
    def test_manager_with_multiple_officers(self):
        """Test that a manager can have multiple collection officers."""
        # Create a new collection officer
        collection_officer3 = User.objects.create_user(
            username='officer3',
            email='officer3@example.com',
            password='password123',
            first_name='Collection',
            last_name='Officer3',
            role=User.Role.COLLECTION_OFFICER
        )
        
        # Create a new hierarchy with an existing manager
        hierarchy = Hierarchy.objects.create(
            manager=self.super_manager,
            collection_officer=collection_officer3
        )
        
        # Check that it was created successfully
        self.assertEqual(Hierarchy.objects.filter(manager=self.super_manager).count(), 2)
        
        # Check that the relationships are correct
        self.assertEqual(hierarchy.manager, self.super_manager)
        self.assertEqual(hierarchy.collection_officer, collection_officer3)
        
    def test_officer_with_multiple_managers(self):
        """Test that a collection officer can have multiple managers."""
        # Create a new hierarchy with an existing collection officer
        hierarchy = Hierarchy.objects.create(
            manager=self.manager,
            collection_officer=self.collection_officer1
        )
        
        # Check that it was created successfully
        self.assertEqual(Hierarchy.objects.filter(collection_officer=self.collection_officer1).count(), 2)
        
        # Check that the relationships are correct
        self.assertEqual(hierarchy.manager, self.manager)
        self.assertEqual(hierarchy.collection_officer, self.collection_officer1)
