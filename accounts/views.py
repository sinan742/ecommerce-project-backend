from django.core.mail import send_mail
from .models import Profile
from rest_framework.response import Response
from .serializers import RegisterSerializer, MyTokenObtainPairSerializer
from rest_framework.views import APIView
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework_simplejwt.views import TokenObtainPairView
from datetime import datetime
from rest_framework.permissions import AllowAny,IsAuthenticated

from django.conf import settings 

class RegisterView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.is_active = False 
            user.save()

            profile, created = Profile.objects.get_or_create(user=user)
            profile.generate_otp()

            try:
                send_mail(
                    'Your Verification Code',
                    f'Your OTP code is {profile.otp}',
                    settings.DEFAULT_FROM_EMAIL, 
                    [user.email],
                    fail_silently=False, 
                )
            except Exception as e:
                print(f"Registration Email Error: {e}")
                return Response({"message": "User created but email failed. Contact support."}, status=status.HTTP_201_CREATED)

            return Response({"message": "OTP sent to your email"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class VerifyOTPView(APIView):
    permission_classes=[AllowAny]

    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')
        
        try:
            user = User.objects.get(email=email)
            profile = user.profile
            
            if str(profile.otp) == str(otp):
                user.is_active = True
                user.save()
                
                profile.otp = None
                profile.save()
                return Response({"message": "Verified!"}, status=status.HTTP_200_OK)
            
            return Response({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        

# login view

class MyTokenObtainPairView(TokenObtainPairView):

    serializer_class = MyTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:

            access_token = response.data.get('accessToken')
            refresh_token = response.data.get('refreshToken')

            print(access_token)
            print(refresh_token)

            response.set_cookie(
                key='accessToken',
                value=access_token,
                httponly=True,  
                secure=False,   
                samesite='Lax',
                path='/',
            )
            response.set_cookie(
                key='refreshToken',
                value=refresh_token,
                httponly=True,
                secure=False,
                samesite='Lax',
                path='/',
            )
            print("Cookies set in response!") # Terminal-
            
        return response

from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.response import Response

class MyTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        # 1. Get the refresh token from the browser's cookies
        refresh_token = request.COOKIES.get('refreshToken')
        
        if refresh_token:
            request.data['refreshToken'] = refresh_token
        
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            new_access = response.data.get('accessToken')
            
            response.set_cookie(
                key='accessToken',
                value=new_access,
                httponly=False,  # Secure!
                secure=False,   # Set True for HTTPS/Production
                samesite='Lax',
                path='/'
            )
            # Remove token from JSON body so it stays invisible to JS
            response.data.pop('accessToken', None)
            
        return response
        
class LogoutView(APIView):

    def post(self, request):
        response = Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)
        
        response.delete_cookie('access',path='/')
        response.delete_cookie('refresh',path='/')
        response.delete_cookie('userName')
       
        
        return response    
    
# forget password

class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email)
            profile = user.profile
            profile.generate_otp()
            
            send_mail(
                'Password Reset OTP',
                f'Your OTP for password reset is: {profile.otp}',
                settings.DEFAULT_FROM_EMAIL, 
                [email],
                fail_silently=False,
            )
            return Response({"message": "OTP sent to your email"}, status=200)
        except User.DoesNotExist:
            return Response({"error": "User with this email not found"}, status=404)

# Reset Password

class ResetPasswordView(APIView):

    permission_classes=[AllowAny]

    def post(self, request):
        email = request.data.get('email')
        otp_received = request.data.get('otp') # data from react
        new_password = request.data.get('new_password')
        
        try:
            user = User.objects.get(email=email)
            profile = user.profile
            
            print(f"DB OTP: {profile.otp} (Type: {type(profile.otp)})")
            print(f"Received OTP: {otp_received} (Type: {type(otp_received)})")

            if str(profile.otp).strip() == str(otp_received).strip():
                user.set_password(new_password)
                user.save()
                
                profile.otp = None 
                profile.save()
                return Response({"message": "Password reset successful"}, status=200)
            else:
                return Response({"error": "Invalid OTP. Please check again."}, status=400)
                
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)
        

# user profile update

class ProfileUpdateView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
        })

    def put(self, request):
        user = request.user
        data = request.data
        
        user.first_name = data.get('first_name', user.first_name)
        user.last_name = data.get('last_name', user.last_name)
        user.email = data.get('email', user.email)
        user.save()
        
        return Response({"message": "Profile updated successfully"})