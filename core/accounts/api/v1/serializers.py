from rest_framework import serializers
from accounts.models import User
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.shortcuts import get_object_or_404
from accounts.models.profiles import Profile


class RegisterSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'confirm_password']

    def validate(self, attrs):
        if attrs.get('password') != attrs.get('confirm_password'):
            raise serializers.ValidationError({'details' : 'password doesnt match...'})
        
        try: 
            validate_password(attrs.get('password'))
        except exceptions.ValidationError as e:
            raise serializers.ValidationError({'password' : list(e.messages)})

        return super().validate(attrs)
    
    def create(self, validated_data):
        validated_data.pop('confirm_password', None)
        return User.objects.create_user(**validated_data)
    

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        validated_data = super().validate(attrs)
        if not self.user.is_verified:
                raise serializers.ValidationError({'detail' : 'user is not verified...'})
        validated_data['email'] = self.user.email
        validated_data['user_id'] = self.user.pk
        return validated_data
    

class ActivationResendSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate(self, attrs):
        email = attrs.get('email')

        try:
            user_obj = get_object_or_404(User, email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({'detail': 'user does not exist'})
        
        if user_obj.is_verified:
            raise serializers.ValidationError({'detail': 'user is already activated and verified'})

        attrs['user'] = user_obj
        return super().validate(attrs)

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    new_password2 = serializers.CharField(required=True)
   
    def validate(self, attrs):
        if attrs.get('new_password') != attrs.get('new_password2'):
            raise serializers.ValidationError({'details' : 'password doesnt match...'})
        
        try: 
            validate_password(attrs.get('new_password'))
        except exceptions.ValidationError as e:
            raise serializers.ValidationError({'new_password' : list(e.messages)})

        return super().validate(attrs)
    

class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        return value

class ResetPasswordConfirmSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True)
    new_password2 = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs.get('new_password') != attrs.get('new_password2'):
            raise serializers.ValidationError({'details' : 'password doesnt match...'})
        
        try: 
            validate_password(attrs.get('new_password'))
        except exceptions.ValidationError as e:
            raise serializers.ValidationError({'new_password' : list(e.messages)})

        return super().validate(attrs)
    
class ProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)
    class Meta:
        model = Profile
        fields = ['email', 'first_name', 'last_name', 'image', 'description']