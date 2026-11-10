from django.contrib.auth import password_validation
from django.contrib.auth.models import User
from django.contrib.auth.validators import UnicodeUsernameValidator
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=150,
        validators=[
            UnicodeUsernameValidator(),
            UniqueValidator(User.objects.all(), message='Користувач з таким username вже існує.'),
        ],
    )
    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True, default='')
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True, default='')
    email = serializers.EmailField(
        max_length=254,
        validators=[UniqueValidator(User.objects.all(), message='Користувач з таким email вже існує.', lookup='iexact')],
    )
    password = serializers.CharField(min_length=8, max_length=128, write_only=True, trim_whitespace=False)
    password_confirm = serializers.CharField(max_length=128, write_only=True, trim_whitespace=False)

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({'password_confirm': 'Паролі не збігаються.'})
        user = User(username=attrs['username'], email=attrs['email'],
                    first_name=attrs['first_name'], last_name=attrs['last_name'])
        try:
            password_validation.validate_password(attrs['password'], user)
        except password_validation.ValidationError as e:
            raise serializers.ValidationError({'password': list(e.messages)})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        return User.objects.create_user(**validated_data)


class UserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'role']

    def get_role(self, user):
        return 'admin' if user.is_staff else 'user'


class LoginSerializer(TokenObtainPairSerializer):
    default_error_messages = {
        'no_active_account': 'Неправильний username або пароль.',
    }
