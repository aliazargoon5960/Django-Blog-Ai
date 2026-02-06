from django.urls import path
from accounts.api.v1 import views
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

app_name = 'api-v1'
urlpatterns = [
    # registration
    path('register/', views.RegisterApiView.as_view(), name='register'),

    # login jwt
    path('jwt/create/', views.CustomTokenObtainPairView.as_view(), name='jwt-create'),
    path('jwt/refresh/', TokenRefreshView.as_view(), name='jwt-refresh'),
    path('jwt/verify/', TokenVerifyView.as_view(), name='jwt-verify'),

    # activation
    path('activation/confirm/<str:token>/', views.ActivationConfirmApiView.as_view(), name='activation-confirm'),

    # resend activation
    path('activation/resend/', views.ActivationResendApiView.as_view(), name='resend_activation'),


    # change password
    path('password/change/', views.ChangePasswordApiView.as_view(), name='change-password'),

    # password reset
    path('password/reset/', views.PasswordResetApiView.as_view(), name='password-reset'),
    path('password/reset/confirm/<str:token>/', views.PasswordResetConfirmApiView.as_view(), name='password-reset-confirm'),


    # profile
    path('profile/', views.UserProfileApiView.as_view(), name='user-profile'),

]