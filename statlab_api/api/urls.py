from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import AbsenceViewSet, UserViewSet


router = DefaultRouter()
router.register('absences', AbsenceViewSet, basename='absences')
router.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
]
