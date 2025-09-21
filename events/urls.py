from django.urls import path
from .views import EventListView, EventDetailView, generate_qr_code, qr_scanner_view, EventCheckinAPI

urlpatterns = [
    path('', EventListView.as_view(), name='event-list'),
    path('<int:event_id>/', EventDetailView.as_view(), name='event-detail'),
    path('<int:event_id>/qr_code/', generate_qr_code, name='event-qr-code'),
    path('scan/', qr_scanner_view, name='event-scanner'),
    # This is the endpoint the scanner will hit
    path('api/checkin/<int:event_id>/', EventCheckinAPI.as_view(), name='api-event-checkin'),
]
