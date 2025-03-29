from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    UserViewSet,
    HierarchyViewSet,
    CustomerViewSet,
    LoanViewSet,
    PaymentViewSet,
    InteractionViewSet,
    FollowUpViewSet,
)

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'hierarchies', HierarchyViewSet, basename='hierarchy')
router.register(r'customers', CustomerViewSet, basename='customer')
router.register(r'loans', LoanViewSet, basename='loan')
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'interactions', InteractionViewSet, basename='interaction')
router.register(r'follow-ups', FollowUpViewSet, basename='follow-up')

# The API URLs are determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
]
