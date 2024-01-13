from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import LoginView, UserAbsencesView, FilteredAbsencesView, AbsenceStatistiquesView
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


router = DefaultRouter()

schema_view = get_schema_view(
   openapi.Info(
        title="Statlab API",
        default_version='v1',
        description="Statlab API for the Statlab project",
        contact=openapi.Contact(email="hugo_goncalves@etu.u-bourgogne.fr"),
        license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('', include(router.urls)),
    path('login/', LoginView.as_view(), name='login'),
    path('absences/', UserAbsencesView.as_view(), name='user_absences'),
    path('absences/filtered/', FilteredAbsencesView.as_view(), name='filtered_absences'),
    path('absences/statistiques/', AbsenceStatistiquesView.as_view(), name='absences_statistiques'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]
