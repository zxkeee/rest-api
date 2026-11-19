import logging

from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from catalog.errors import error_response
from catalog.serializers import ErrorSerializer

from .serializers import LoginSerializer, RegisterSerializer, UserSerializer

logger = logging.getLogger(__name__)

VALIDATION_DETAIL = 'Невалідні дані. Деталі в полі errors.'


class RegisterView(APIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    @extend_schema(responses={201: UserSerializer, 400: ErrorSerializer})
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            logger.info('Registration rejected: fields %s', list(serializer.errors))
            return error_response(status.HTTP_400_BAD_REQUEST, VALIDATION_DETAIL, serializer.errors)
        user = serializer.save()
        logger.info('User id=%s registered', user.pk)
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


@extend_schema(
    responses={
        200: inline_serializer('TokenPair', {'access': serializers.CharField(), 'refresh': serializers.CharField()}),
        401: ErrorSerializer,
    },
)
class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer


class LogoutView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=inline_serializer('LogoutRequest', {'refresh': serializers.CharField()}),
        responses={205: None, 400: ErrorSerializer, 401: ErrorSerializer},
    )
    def post(self, request):
        refresh = request.data.get('refresh')
        if not refresh:
            return error_response(status.HTTP_400_BAD_REQUEST, VALIDATION_DETAIL, {'refresh': ['Це поле обовʼязкове.']})
        try:
            RefreshToken(refresh).blacklist()
        except TokenError:
            logger.warning('Logout with invalid refresh token')
            return error_response(status.HTTP_401_UNAUTHORIZED, 'Refresh токен недійсний або прострочений.')
        logger.info('Refresh token blacklisted on logout')
        return Response(status=status.HTTP_205_RESET_CONTENT)


class MeView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get(self, request):
        return Response(UserSerializer(request.user).data)
