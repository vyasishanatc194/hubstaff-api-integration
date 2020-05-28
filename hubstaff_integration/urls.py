from django.urls import path
from hubstaff_integration.views import HubStaffUsers, DashBoardView

urlpatterns = [
    path('', DashBoardView.as_view(), name='dashboard-view'),
    path('api/v1/hubstaff/users/', HubStaffUsers.as_view(), name="api-hub-staff-users"),
]
