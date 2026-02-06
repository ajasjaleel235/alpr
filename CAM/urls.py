from django.urls import path
# We now import the new unified view and the trigger function
from .views import unified_dashboard, trigger_processing

urlpatterns = [
    # Homepage (The Unified Dashboard)
    path('', unified_dashboard, name='dashboard'),
    path('dashboard/', unified_dashboard, name='dashboard_alias'),
    
    # The Action Button (Trigger AI Scan)
    path('trigger_scan/', trigger_processing, name='trigger_scan'),
]