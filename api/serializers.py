from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _

from users.models import User, Hierarchy
from customers.models import Customer
from loans.models import Loan, Payment
from interactions.models import Interaction, FollowUp


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the User model"""
    
    password = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 
                  'phone', 'role', 'password', 'is_active', 'date_joined')
        read_only_fields = ('id', 'date_joined')
        extra_kwargs = {
            'password': {'write_only': True},
        }
    
    def validate_password(self, value):
        validate_password(value)
        return value
    
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        
        if password:
            user.set_password(password)
            user.save()
        
        return user


class HierarchySerializer(serializers.ModelSerializer):
    """Serializer for the Hierarchy model"""
    
    manager_name = serializers.SerializerMethodField()
    collection_officer_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Hierarchy
        fields = ('id', 'manager', 'manager_name', 
                  'collection_officer', 'collection_officer_name',
                  'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')
    
    def get_manager_name(self, obj):
        return obj.manager.get_full_name()
    
    def get_collection_officer_name(self, obj):
        return obj.collection_officer.get_full_name()
    
    def validate(self, data):
        if 'manager' in data and 'collection_officer' in data:
            if data['manager'] == data['collection_officer']:
                raise serializers.ValidationError(_("A user cannot be their own manager."))
            
            if data['manager'].role not in [User.Role.MANAGER, User.Role.SUPER_MANAGER]:
                raise serializers.ValidationError(_("Manager must have Manager or Super Manager role."))
                
            if data['collection_officer'].role != User.Role.COLLECTION_OFFICER:
                raise serializers.ValidationError(_("Collection officer must have Collection Officer role."))
        
        return data


class CustomerSerializer(serializers.ModelSerializer):
    """Serializer for the Customer model"""
    
    assigned_officer_name = serializers.SerializerMethodField()
    gender_display = serializers.CharField(source='get_gender_display', read_only=True)
    
    class Meta:
        model = Customer
        fields = ('id', 'first_name', 'last_name', 'gender', 'gender_display',
                  'date_of_birth', 'national_id', 'primary_phone', 'secondary_phone',
                  'email', 'address', 'city', 'state', 'postal_code', 'country', 'branch',
                  'employer', 'job_title', 'monthly_income', 'assigned_officer',
                  'assigned_officer_name', 'is_active', 'paid_status', 'notes', 'risk_score',
                  'created_at', 'updated_at', 'created_by', 'updated_by')
        read_only_fields = ('id', 'created_at', 'updated_at', 'created_by', 'updated_by')
    
    def get_assigned_officer_name(self, obj):
        if obj.assigned_officer:
            return obj.assigned_officer.get_full_name()
        return None
    
    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['created_by'] = request.user
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['updated_by'] = request.user
        return super().update(instance, validated_data)


class LoanSerializer(serializers.ModelSerializer):
    """Serializer for the Loan model"""
    
    customer_name = serializers.SerializerMethodField()
    assigned_officer_name = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_frequency_display = serializers.CharField(source='get_payment_frequency_display', read_only=True)
    total_amount_due = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    remaining_balance = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    payment_status = serializers.CharField(read_only=True)
    
    class Meta:
        model = Loan
        fields = ('id', 'customer', 'customer_name', 'loan_reference', 'status', 'status_display',
                  'principal_amount', 'interest_rate', 'application_date', 'approval_date',
                  'disbursement_date', 'first_payment_date', 'maturity_date', 'term_months',
                  'payment_frequency', 'payment_frequency_display', 'amount_paid', 'last_payment_date',
                  'days_past_due', 'assigned_officer', 'assigned_officer_name', 'notes',
                  'total_amount_due', 'remaining_balance', 'payment_status',
                  'created_at', 'updated_at', 'created_by', 'updated_by')
        read_only_fields = ('id', 'loan_reference', 'amount_paid', 'last_payment_date',
                           'created_at', 'updated_at', 'created_by', 'updated_by')
    
    def get_customer_name(self, obj):
        return obj.customer.full_name
    
    def get_assigned_officer_name(self, obj):
        if obj.assigned_officer:
            return obj.assigned_officer.get_full_name()
        return None
    
    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['created_by'] = request.user
            
            # Generate a unique loan reference
            import uuid
            validated_data['loan_reference'] = f"LN-{str(uuid.uuid4())[:8].upper()}"
            
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['updated_by'] = request.user
        return super().update(instance, validated_data)


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for the Payment model"""
    
    loan_reference = serializers.CharField(source='loan.loan_reference', read_only=True)
    customer_name = serializers.CharField(source='loan.customer.full_name', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    received_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Payment
        fields = ('id', 'loan', 'loan_reference', 'customer_name', 'payment_reference',
                  'amount', 'payment_date', 'payment_method', 'payment_method_display',
                  'received_by', 'received_by_name', 'notes',
                  'created_at', 'updated_at')
        read_only_fields = ('id', 'payment_reference', 'created_at', 'updated_at')
    
    def get_received_by_name(self, obj):
        if obj.received_by:
            return obj.received_by.get_full_name()
        return None
    
    def create(self, validated_data):
        # Generate a unique payment reference
        import uuid
        validated_data['payment_reference'] = f"PMT-{str(uuid.uuid4())[:8].upper()}"
        
        # Use the current user as the receiver if not specified
        if 'received_by' not in validated_data:
            request = self.context.get('request')
            if request and hasattr(request, 'user'):
                validated_data['received_by'] = request.user
        
        return super().create(validated_data)


class InteractionSerializer(serializers.ModelSerializer):
    """Serializer for the Interaction model"""
    
    customer_name = serializers.CharField(source='customer.full_name', read_only=True)
    loan_reference = serializers.CharField(source='loan.loan_reference', read_only=True)
    initiated_by_name = serializers.SerializerMethodField()
    interaction_type_display = serializers.CharField(source='get_interaction_type_display', read_only=True)
    outcome_display = serializers.CharField(source='get_outcome_display', read_only=True)
    
    class Meta:
        model = Interaction
        fields = ('id', 'customer', 'customer_name', 'loan', 'loan_reference',
                  'interaction_type', 'interaction_type_display', 'initiated_by', 'initiated_by_name',
                  'contact_number', 'contact_person', 'start_time', 'end_time', 'duration',
                  'outcome', 'outcome_display', 'notes', 'payment_promise_amount', 'payment_promise_date',
                  'created_at', 'updated_at')
        read_only_fields = ('id', 'duration', 'created_at', 'updated_at')
    
    def get_initiated_by_name(self, obj):
        return obj.initiated_by.get_full_name()
    
    def create(self, validated_data):
        if 'initiated_by' not in validated_data:
            request = self.context.get('request')
            if request and hasattr(request, 'user'):
                validated_data['initiated_by'] = request.user
        
        return super().create(validated_data)


class FollowUpSerializer(serializers.ModelSerializer):
    """Serializer for the FollowUp model"""
    
    customer_name = serializers.CharField(source='customer.full_name', read_only=True)
    assigned_to_name = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()
    completed_by_name = serializers.SerializerMethodField()
    follow_up_type_display = serializers.CharField(source='get_follow_up_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    
    class Meta:
        model = FollowUp
        fields = ('id', 'interaction', 'customer', 'customer_name', 'follow_up_type', 'follow_up_type_display',
                  'scheduled_date', 'scheduled_time', 'assigned_to', 'assigned_to_name',
                  'notes', 'priority', 'priority_display', 'status', 'status_display',
                  'result', 'completed_at', 'completed_by', 'completed_by_name',
                  'created_at', 'updated_at', 'created_by', 'created_by_name')
        read_only_fields = ('id', 'created_at', 'updated_at', 'created_by')
    
    def get_assigned_to_name(self, obj):
        return obj.assigned_to.get_full_name()
    
    def get_created_by_name(self, obj):
        return obj.created_by.get_full_name()
    
    def get_completed_by_name(self, obj):
        if obj.completed_by:
            return obj.completed_by.get_full_name()
        return None
    
    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['created_by'] = request.user
        
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        # If status is being changed to COMPLETED, set completed_at and completed_by
        if 'status' in validated_data and validated_data['status'] == FollowUp.FollowUpStatus.COMPLETED:
            from django.utils import timezone
            validated_data['completed_at'] = timezone.now()
            
            request = self.context.get('request')
            if request and hasattr(request, 'user'):
                validated_data['completed_by'] = request.user
        
        return super().update(instance, validated_data) 