from django.urls import path
from .views import process_survey, get_activity, get_survey_history

urlpatterns = [
    path('survey/', process_survey, name='process_survey'),
    path('activity/', get_activity, name='get_activity'),
    path('history/', get_survey_history, name='survey_history'),
]
