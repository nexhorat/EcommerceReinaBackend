from django.urls import path,include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView, 
    CustomTokenObtainPairView, 
    UserProfileView, 
    RoleManagementViewSet,
    UserRoleAssignmentViewSet,
    PasswordResetConfirmView,
    PasswordResetRequestView
) 

# Definición manual de acciones para Roles (Grupos)
role_list = RoleManagementViewSet.as_view({'get': 'list', 'post': 'create'})
role_detail = RoleManagementViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'})
permisos_list = RoleManagementViewSet.as_view({'get': 'permisos_disponibles'})

# Definición manual de acciones para Asignación de Usuarios
user_assign_list = UserRoleAssignmentViewSet.as_view({'get': 'list'})
user_assign_detail = UserRoleAssignmentViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update'})

urlpatterns = [
    path('register/', RegisterView.as_view(), name='auth_register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='auth_login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='auth_token_refresh'),
    path('perfil/', UserProfileView.as_view(), name='user-profile'),
    path('roles/', role_list, name='roles-list'),                     
    path('roles/<int:pk>/', role_detail, name='roles-detail'),        
    path('roles/permisos/', permisos_list, name='permisos-list'),     
    path('gestion-usuarios/', user_assign_list, name='user-assign-list'),       
    path('gestion-usuarios/<int:pk>/', user_assign_detail, name='user-assign-detail'), 
    path('password-reset/', PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('perfil/password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
]

