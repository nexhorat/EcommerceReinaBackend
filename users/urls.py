from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView, 
    CustomTokenObtainPairView, 
    UserProfileView, 
    ChangePasswordView
) 

urlpatterns = [
    path('register/', RegisterView.as_view(), name='auth_register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='auth_login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='auth_token_refresh'),
    path('perfil/', UserProfileView.as_view(), name='user-profile'),
    path('perfil/cambiar-password/', ChangePasswordView.as_view(), name='change-password'),
]