from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from catalog.errors import error_response

from .serializers import LoginSerializer, RegisterSerializer, UserSerializer

VALIDATION_DETAIL = 'Невалідні дані. Деталі в полі errors.'


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(status.HTTP_400_BAD_REQUEST, VALIDATION_DETAIL, serializer.errors)
        user = serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer


class LogoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        refresh = request.data.get('refresh')
        if not refresh:
            return error_response(status.HTTP_400_BAD_REQUEST, VALIDATION_DETAIL, {'refresh': ['Це поле обовʼязкове.']})
        try:
            RefreshToken(refresh).blacklist()
        except TokenError:
            return error_response(status.HTTP_401_UNAUTHORIZED, 'Refresh токен недійсний або прострочений.')
        return Response(status=status.HTTP_205_RESET_CONTENT)


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)
