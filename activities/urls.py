from django.urls import path
from .views import SubmitActivityView

urlpatterns = [
    path('submit/', SubmitActivityView.as_view(), name='submit-activity'),
]
