from django.urls import path
from .views import process_survey, get_activity

urlpatterns = [
    path("process-survey/", process_survey, name="process-survey"),
    path("get-activity/", get_activity, name="get-activity"),
]
