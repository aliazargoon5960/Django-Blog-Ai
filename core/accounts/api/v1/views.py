from rest_framework.response import Response
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.generics import GenericAPIView, RetrieveUpdateAPIView
from .serializers import (RegisterSerializer, CustomTokenObtainPairSerializer, ActivationResendSerializer,
                           ChangePasswordSerializer,PasswordResetSerializer, ResetPasswordConfirmSerializer, ProfileSerializer)
from rest_framework_simplejwt.views import TokenObtainPairView
import jwt
from django.conf import settings
from jwt.exceptions import ExpiredSignatureError, InvalidSignatureError
from django.shortcuts import get_object_or_404
from mail_templated import EmailMessage
from .utils import EmailThread
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated
from datetime import datetime, timedelta
from accounts.models.profiles import Profile


User = get_user_model()

class RegisterApiView(GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            email = serializer.validated_data['email']
            data = {'email' : email}
            user_obj = get_object_or_404(User, email=email)
            token = self.get_tokens_for_user(user_obj)
            email_obj = EmailMessage('email/activation_email.tpl', {'token' : token}, 'admin@gmail.com', to=[email])
            EmailThread(email_obj).start()
            return Response(data, status=status.HTTP_201_CREATED) 
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get_tokens_for_user(self,user):
        if not user.is_active:
            raise AuthenticationFailed("User is not active")

        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)
    

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class ActivationConfirmApiView(GenericAPIView):
    def get(self, request,token,*args, **kwargs):
        try:
            token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id  = token.get("user_id")
        except ExpiredSignatureError:
            return Response({'details' : 'token has been expired'}, status=status.HTTP_400_BAD_REQUEST)
        except InvalidSignatureError:
            return Response({'details' : 'token is not valid'}, status=status.HTTP_400_BAD_REQUEST)
        
        user_obj = get_object_or_404(User, pk=user_id)
        if user_obj.is_verified:
            return Response({'details' : 'user is already activated and verified'})
        user_obj.is_verified = True
        user_obj.save()
        return Response({'details' : 'your account have been verified'}, status=status.HTTP_200_OK)
    

class ActivationResendApiView(GenericAPIView):
    serializer_class = ActivationResendSerializer
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_obj = serializer.validated_data['user']
        token = self.get_tokens_for_user(user_obj)
        email_obj = EmailMessage('email/activation_email.tpl', {'token' : token}, 'admin@gmail.com', to=[user_obj.email])
        EmailThread(email_obj).start()
        return Response({'details' : 'user activation resend successfully'}, status=status.HTTP_200_OK)

    
    def get_tokens_for_user(self,user):
        if not user.is_active:
            raise AuthenticationFailed("User is not active")

        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)
    


class ChangePasswordApiView(GenericAPIView):
    model = User
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj
    
    def put(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            if self.object.check_password(serializer.data.get('old_password')) == False:
                return Response({"old_password" : "Wrong password..."}, status=status.HTTP_400_BAD_REQUEST)
            self.object.set_password(serializer.data.get('new_password'))
            self.object.save()
            return Response({'details' : 'password change successfully'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class PasswordResetApiView(GenericAPIView):
    serializer_class = PasswordResetSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        user_obj = get_object_or_404(User, email=email)
        if user_obj:
            token = self.get_tokens_for_user(user_obj)
            email_obj = EmailMessage('email/reset_password.tpl', {'token' : token}, 'admin@gmail.com', to=[email])
            EmailThread(email_obj).start()
            return Response({'details' : 'reset link has been sent.'}, status=status.HTTP_200_OK)
        
        return Response({'details' : 'user does not exists.'}, status=status.HTTP_404_NOT_FOUND)
        
       
    def get_tokens_for_user(self, user):
        payload = {
            "user_id": user.id,
            "token_type": "reset_password",
            "exp": datetime.utcnow() + timedelta(minutes=10)
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
        return token
    
class PasswordResetConfirmApiView(GenericAPIView):
   serializer_class = ResetPasswordConfirmSerializer

   def post(self, request, token, *args, **kwargs):
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            if payload.get("token_type") != "reset_password":
                return Response({'details' : 'Invalid token type'}, status=status.HTTP_400_BAD_REQUEST)
            
            user_id = payload.get('user_id')

        except ExpiredSignatureError:
            return Response({'details': 'Token has expired'},status=status.HTTP_400_BAD_REQUEST)
        except InvalidSignatureError:
            return Response({'details': 'Invalid token'},status=status.HTTP_400_BAD_REQUEST)
        
        user_obj = get_object_or_404(User, pk=user_id)

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_obj.set_password(serializer.validated_data['new_password'])
        user_obj.save()

        return Response({'details' : 'Password reset successfully'}, status=status.HTTP_200_OK) 
   

class UserProfileApiView(RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    queryset = Profile.objects.all()

    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, user=self.request.user)
        return obj
