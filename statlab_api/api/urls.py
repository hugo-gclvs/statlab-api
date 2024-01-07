from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import AbsenceViewSet, UserViewSet, LoginView


router = DefaultRouter()
router.register('absences', AbsenceViewSet, basename='absences')
router.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
    path('login/', LoginView.as_view(), name='login'),
]
