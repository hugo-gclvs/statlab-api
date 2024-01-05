from django.urls import path
from .views import AbsenceList

urlpatterns = [
    path('absences/', AbsenceList.as_view(), name='absence-list'),
]
