from django.urls import path
from .views import (
    DashboardView, LeaderboardView, AICalculatorView, carbon_chart_data, carbon_pie_chart_data, chatbot_api,
    ai_recommendation_api, carbon_prediction_api, efficiency_insights_api,
    generate_challenge_api, update_challenge_progress_api,
    ai_calculator_api, ai_calculator_compound_api, ai_calculator_predict_api
)

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('leaderboard/', LeaderboardView.as_view(), name='leaderboard'),
    path('ai-calculator/', AICalculatorView.as_view(), name='ai-calculator'),
    path('api/carbon-chart-data/', carbon_chart_data, name='carbon-chart-data'),
    path('api/carbon-pie-chart-data/', carbon_pie_chart_data, name='carbon-pie-chart-data'),
    path('api/chatbot/', chatbot_api, name='chatbot-api'),
    # AI Feature APIs
    path('api/ai-recommendation/', ai_recommendation_api, name='ai-recommendation-api'),
    path('api/carbon-prediction/', carbon_prediction_api, name='carbon-prediction-api'),
    path('api/efficiency-insights/', efficiency_insights_api, name='efficiency-insights-api'),
    path('api/generate-challenge/', generate_challenge_api, name='generate-challenge-api'),
    path('api/update-challenge-progress/', update_challenge_progress_api, name='update-challenge-progress-api'),
    # AI Calculator APIs
    path('api/ai-calculator/', ai_calculator_api, name='ai-calculator-api'),
    path('api/ai-calculator/compound/', ai_calculator_compound_api, name='ai-calculator-compound-api'),
    path('api/ai-calculator/predict/', ai_calculator_predict_api, name='ai-calculator-predict-api'),
]
