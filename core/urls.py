from django.urls import path
from .views import HomePageView, global_chatbot_api

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('api/chatbot/', global_chatbot_api, name='global-chatbot-api'),
]
