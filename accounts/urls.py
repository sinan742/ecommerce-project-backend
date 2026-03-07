from .views import RegisterView,VerifyOTPView,MyTokenObtainPairView,ForgotPasswordView,ResetPasswordView,LogoutView,ProfileUpdateView,MyTokenRefreshView
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns=[
    path('register/',RegisterView.as_view()),
    path('verify-otp/', VerifyOTPView.as_view()),
    path('login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/refresh/', ResetPasswordView.as_view(), name='token_refresh'),
    path('forgot-password/',ForgotPasswordView.as_view(),name='forget-password'),
    path('reset-password/',ResetPasswordView.as_view(),name='reset-password'),
    path('profile/',ProfileUpdateView.as_view())
]