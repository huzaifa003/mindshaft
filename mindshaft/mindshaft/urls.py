from django.contrib import admin
from django.urls import path, include  # Include function for modular URLs
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    # Admin route
    path("admin/", admin.site.urls),
    
    # JWT Authentication
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/token/verify/", TokenVerifyView.as_view(), name="token_verify"),  # <-- Add the verify token path
    
    # App-specific routes
    path("api/users/", include("users.urls")),  # Include URLs from the users app
    path("api/chats/", include("chats.urls")),  # Include URLs from the chats app
    path('api/rag/', include('rag.urls')),  # Include URLs from the rag app

    path('api/billing/', include('billing.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)