from django.urls import path
from .views import RegisterView, UserDetailView, CustomTokenObtainPairView # Importa tu custom view
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='auth_register'),
    
    # Usamos nuestra vista personalizada para que aparezca documentada
    path('login/', CustomTokenObtainPairView.as_view(), name='auth_login'),
    
    path('token/refresh/', TokenRefreshView.as_view(), name='auth_token_refresh'),
    path('me/', UserDetailView.as_view(), name='auth_me'),
]