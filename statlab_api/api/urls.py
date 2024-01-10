from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, LoginView, UserAbsencesView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

router = DefaultRouter()
# router.register('absences', AbsenceViewSet, basename='absences')
router.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
    path('login/', LoginView.as_view(), name='login'),
    path('absences/', UserAbsencesView.as_view(), name='user_absences'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
  
]
