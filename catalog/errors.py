from rest_framework.exceptions import NotAuthenticated
from rest_framework.response import Response
from rest_framework.views import exception_handler
from rest_framework_simplejwt.exceptions import InvalidToken


def error_response(status_code, detail, errors=None):
    return Response({'status': status_code, 'detail': detail, 'errors': errors}, status=status_code)


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        return None
    if isinstance(exc, NotAuthenticated):
        detail = 'Потрібна авторизація. Передайте access токен у заголовку Authorization: Bearer <token>.'
        errors = None
    elif isinstance(exc, InvalidToken):
        detail = 'Токен недійсний або прострочений.'
        errors = None
    elif isinstance(response.data, dict) and 'detail' in response.data:
        detail = str(response.data['detail'])
        errors = None
    else:
        detail = 'Невалідні дані. Деталі в полі errors.'
        errors = response.data
    response.data = {'status': response.status_code, 'detail': detail, 'errors': errors}
    return response


def plural(count, one, few, many):
    if count % 10 == 1 and count % 100 != 11:
        word = one
    elif 2 <= count % 10 <= 4 and not 12 <= count % 100 <= 14:
        word = few
    else:
        word = many
    return f'{count} {word}'
