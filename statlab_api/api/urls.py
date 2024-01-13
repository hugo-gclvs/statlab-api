from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import LoginView, UserAbsencesView, FilteredAbsencesView, AbsenceStatistiquesView
from rest_framework_simplejwt.views import TokenRefreshView


router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path('login/', LoginView.as_view(), name='login'),
    path('absences/', UserAbsencesView.as_view(), name='user_absences'),
    path('absences/filtered/', FilteredAbsencesView.as_view(), name='filtered_absences'),
    path('absences/statistiques/', AbsenceStatistiquesView.as_view(), name='absences_statistiques'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
