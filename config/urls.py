"""
URL configuration for Real-Time Chat project.
"""

from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)

urlpatterns = [
    # Django Admin paneli
    path('admin/', admin.site.urls),

    # SimpleJWT autentifikatsiya endpointlari
    # POST /api/token/ -> username va password orqali access va refresh token olish
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # POST /api/token/refresh/ -> refresh token orqali yangi access token olish
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Swagger va OpenAPI Schema endpointlari
    # /api/schema/ -> OpenAPI v3 JSON sxemasi
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # /api/docs/ -> Chiroyli Swagger UI interfeysi
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    # Websocket ilovasi URL-lari (Frontend sahifasi va /api/messages/)
    path('', include('websocket.urls')),
]
