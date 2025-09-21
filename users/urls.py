from django.urls import path, include
from .views import SignUpView, UserProfileView, generate_certificate_pdf
from .test_oauth import test_oauth_urls

urlpatterns = [
    # Use Django's built-in auth views
    path('', include('django.contrib.auth.urls')),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('certificate/', generate_certificate_pdf, name='generate-certificate'),
    path('test-oauth/', test_oauth_urls, name='test_oauth'),
]
