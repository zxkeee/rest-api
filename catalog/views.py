import logging

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView

from users.permissions import IsAdminOrReadOnly, IssuePermission

from .errors import error_response, plural
from .models import DIFFICULTY_CHOICES, ISSUE_STATUS_CHOICES, Issue, Language, Maintainer, Organization, Project
from .serializers import ErrorSerializer, IssueSerializer, LanguageSerializer, MaintainerSerializer, OrganizationSerializer, ProjectSerializer

logger = logging.getLogger(__name__)

PROJECT_ORDERING = ['name', '-name', 'stars', '-stars']
DIFFICULTIES = [choice[0] for choice in DIFFICULTY_CHOICES]
ISSUE_STATUSES = [choice[0] for choice in ISSUE_STATUS_CHOICES]


def validation_error(serializer):
    logger.info('Validation failed for %s: fields %s', serializer.__class__.__name__, list(serializer.errors))
    return error_response(status.HTTP_400_BAD_REQUEST, 'Невалідні дані. Деталі в полі errors.', serializer.errors)


def save(serializer, request, code=status.HTTP_200_OK):
    if not serializer.is_valid():
        return validation_error(serializer)
    obj = serializer.save()
    action = 'created' if code == status.HTTP_201_CREATED else 'updated'
    logger.info('%s id=%s %s by user id=%s', type(obj).__name__, obj.pk, action, request.user.pk)
    return Response(serializer.data, status=code)


def destroy(obj, request):
    logger.info('%s id=%s deleted by user id=%s', type(obj).__name__, obj.pk, request.user.pk)
    obj.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


def conflict(detail):
    logger.warning(detail)
    return error_response(status.HTTP_409_CONFLICT, detail)


class LanguageList(APIView):
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = LanguageSerializer

    @extend_schema(responses=LanguageSerializer(many=True))
    def get(self, request):
        languages = Language.objects.all()
        serializer = LanguageSerializer(languages, many=True)
        return Response(serializer.data)

    def post(self, request):
        return save(LanguageSerializer(data=request.data), request, status.HTTP_201_CREATED)


class LanguageDetail(APIView):
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = LanguageSerializer

    def get_object(self, pk):
        try:
            return Language.objects.get(pk=pk)
        except Language.DoesNotExist:
            raise NotFound(f'Мову з id={pk} не знайдено.')

    def get(self, request, pk):
        language = self.get_object(pk)
        serializer = LanguageSerializer(language)
        return Response(serializer.data)

    def patch(self, request, pk):
        return save(LanguageSerializer(self.get_object(pk), data=request.data, partial=True), request)

    def delete(self, request, pk):
        language = self.get_object(pk)
        projects_count = language.projects.count()
        if projects_count > 0:
            return conflict(
                f'Неможливо видалити мову «{language.name}», оскільки її використовують '
                f'{plural(projects_count, "проєкт", "проєкти", "проєктів")}. '
                f'Спочатку приберіть цю мову з проєктів.'
            )
        return destroy(language, request)


class OrganizationList(APIView):
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = OrganizationSerializer

    @extend_schema(responses=OrganizationSerializer(many=True))
    def get(self, request):
        organizations = Organization.objects.all()
        search = request.query_params.get('search')
        if search:
            organizations = organizations.filter(name__icontains=search)
        serializer = OrganizationSerializer(organizations, many=True)
        return Response(serializer.data)

    def post(self, request):
        return save(OrganizationSerializer(data=request.data), request, status.HTTP_201_CREATED)


class OrganizationDetail(APIView):
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = OrganizationSerializer

    def get_object(self, pk):
        try:
            return Organization.objects.get(pk=pk)
        except Organization.DoesNotExist:
            raise NotFound(f'Організацію з id={pk} не знайдено.')

    def get(self, request, pk):
        organization = self.get_object(pk)
        serializer = OrganizationSerializer(organization)
        return Response(serializer.data)

    def patch(self, request, pk):
        return save(OrganizationSerializer(self.get_object(pk), data=request.data, partial=True), request)

    def delete(self, request, pk):
        organization = self.get_object(pk)
        projects_count = organization.projects.count()
        if projects_count > 0:
            return conflict(
                f'Неможливо видалити організацію «{organization.name}», оскільки за нею закріплено '
                f'{plural(projects_count, "проєкт", "проєкти", "проєктів")}. '
                f'Спочатку видаліть ці проєкти або перенесіть їх в іншу організацію.'
            )
        return destroy(organization, request)


class OrganizationProjects(APIView):
    serializer_class = ProjectSerializer

    @extend_schema(responses=ProjectSerializer(many=True))
    def get(self, request, pk):
        try:
            organization = Organization.objects.get(pk=pk)
        except Organization.DoesNotExist:
            raise NotFound(f'Організацію з id={pk} не знайдено.')
        serializer = ProjectSerializer(organization.projects.all(), many=True)
        return Response(serializer.data)


class MaintainerList(APIView):
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = MaintainerSerializer

    @extend_schema(responses=MaintainerSerializer(many=True))
    def get(self, request):
        maintainers = Maintainer.objects.all()
        search = request.query_params.get('search')
        if search:
            maintainers = maintainers.filter(full_name__icontains=search)
        serializer = MaintainerSerializer(maintainers, many=True)
        return Response(serializer.data)

    def post(self, request):
        return save(MaintainerSerializer(data=request.data), request, status.HTTP_201_CREATED)


class MaintainerDetail(APIView):
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = MaintainerSerializer

    def get_object(self, pk):
        try:
            return Maintainer.objects.get(pk=pk)
        except Maintainer.DoesNotExist:
            raise NotFound(f'Мейнтейнера з id={pk} не знайдено.')

    def get(self, request, pk):
        maintainer = self.get_object(pk)
        serializer = MaintainerSerializer(maintainer)
        return Response(serializer.data)

    def patch(self, request, pk):
        return save(MaintainerSerializer(self.get_object(pk), data=request.data, partial=True), request)

    def delete(self, request, pk):
        maintainer = self.get_object(pk)
        projects_count = maintainer.projects.count()
        if projects_count > 0:
            return conflict(
                f'Неможливо видалити мейнтейнера «{maintainer.full_name}», оскільки за ним закріплено '
                f'{plural(projects_count, "проєкт", "проєкти", "проєктів")}. '
                f'Спочатку призначте цим проєктам іншого мейнтейнера.'
            )
        return destroy(maintainer, request)


class MaintainerProjects(APIView):
    serializer_class = ProjectSerializer

    @extend_schema(responses=ProjectSerializer(many=True))
    def get(self, request, pk):
        try:
            maintainer = Maintainer.objects.get(pk=pk)
        except Maintainer.DoesNotExist:
            raise NotFound(f'Мейнтейнера з id={pk} не знайдено.')
        serializer = ProjectSerializer(maintainer.projects.all(), many=True)
        return Response(serializer.data)


class ProjectList(APIView):
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = ProjectSerializer

    @extend_schema(responses=ProjectSerializer(many=True))
    def get(self, request):
        projects = Project.objects.all()
        search = request.query_params.get('search')
        language = request.query_params.get('language')
        difficulty = request.query_params.get('difficulty')
        ordering = request.query_params.get('ordering')
        if difficulty and difficulty not in DIFFICULTIES:
            return error_response(
                status.HTTP_400_BAD_REQUEST,
                f'Невідомий рівень складності «{difficulty}». Допустимі значення: {", ".join(DIFFICULTIES)}.',
            )
        if ordering and ordering not in PROJECT_ORDERING:
            return error_response(
                status.HTTP_400_BAD_REQUEST,
                f'Неможливо відсортувати за «{ordering}». Допустимі значення: {", ".join(PROJECT_ORDERING)}.',
            )
        if search:
            projects = projects.filter(name__icontains=search)
        if language:
            projects = projects.filter(languages__name__iexact=language)
        if difficulty:
            projects = projects.filter(difficulty=difficulty)
        if ordering:
            projects = projects.order_by(ordering)
        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data)

    def post(self, request):
        return save(ProjectSerializer(data=request.data), request, status.HTTP_201_CREATED)


class ProjectDetail(APIView):
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = ProjectSerializer

    def get_object(self, pk):
        try:
            return Project.objects.get(pk=pk)
        except Project.DoesNotExist:
            raise NotFound(f'Проєкт з id={pk} не знайдено.')

    def get(self, request, pk):
        project = self.get_object(pk)
        serializer = ProjectSerializer(project)
        return Response(serializer.data)

    def patch(self, request, pk):
        return save(ProjectSerializer(self.get_object(pk), data=request.data, partial=True), request)

    def delete(self, request, pk):
        project = self.get_object(pk)
        open_issues_count = project.issues.filter(status__in=['open', 'in_progress']).count()
        if open_issues_count > 0:
            return conflict(
                f'Неможливо видалити проєкт «{project.name}», оскільки він має '
                f'{plural(open_issues_count, "незакриту задачу", "незакриті задачі", "незакритих задач")}. '
                f'Спочатку закрийте або видаліть їх.'
            )
        return destroy(project, request)


def error(description):
    return OpenApiResponse(ErrorSerializer, description=description)


ISSUE_EXAMPLE = OpenApiExample(
    'Задача',
    value={'project': 1, 'title': 'Add type hints to utils', 'difficulty': 'beginner', 'status': 'open'},
    request_only=True,
)
NOT_FOUND = error('Задачу не знайдено')
NO_TOKEN = error('Немає токена або він недійсний')
INVALID = error('Невалідні дані, помилки по полях у errors')


@extend_schema(tags=['issues'])
class IssueList(APIView):
    permission_classes = [IssuePermission]
    serializer_class = IssueSerializer

    @extend_schema(
        summary='Список задач',
        description='Доступно без авторизації. Фільтри можна комбінувати.',
        parameters=[
            OpenApiParameter('difficulty', enum=DIFFICULTIES, description='Рівень складності'),
            OpenApiParameter('status', enum=ISSUE_STATUSES, description='Статус задачі'),
            OpenApiParameter('project', OpenApiTypes.INT, description='id проєкту'),
        ],
        responses={200: IssueSerializer(many=True), 400: error('Невідоме значення фільтра')},
    )
    def get(self, request):
        issues = Issue.objects.all()
        difficulty = request.query_params.get('difficulty')
        issue_status = request.query_params.get('status')
        project = request.query_params.get('project')
        if difficulty and difficulty not in DIFFICULTIES:
            return error_response(
                status.HTTP_400_BAD_REQUEST,
                f'Невідомий рівень складності «{difficulty}». Допустимі значення: {", ".join(DIFFICULTIES)}.',
            )
        if issue_status and issue_status not in ISSUE_STATUSES:
            return error_response(
                status.HTTP_400_BAD_REQUEST,
                f'Невідомий статус «{issue_status}». Допустимі значення: {", ".join(ISSUE_STATUSES)}.',
            )
        if project and not project.isdigit():
            return error_response(status.HTTP_400_BAD_REQUEST, 'Параметр project має бути числом (id проєкту).')
        if difficulty:
            issues = issues.filter(difficulty=difficulty)
        if issue_status:
            issues = issues.filter(status=issue_status)
        if project:
            issues = issues.filter(project_id=project)
        serializer = IssueSerializer(issues, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary='Створити задачу',
        description='Потрібен access токен. Доступно будь-якому залогіненому користувачу.',
        examples=[ISSUE_EXAMPLE],
        responses={201: IssueSerializer, 400: INVALID, 401: NO_TOKEN},
    )
    def post(self, request):
        return save(IssueSerializer(data=request.data), request, status.HTTP_201_CREATED)


@extend_schema(tags=['issues'])
class IssueDetail(APIView):
    permission_classes = [IssuePermission]
    serializer_class = IssueSerializer

    def get_object(self, pk):
        try:
            return Issue.objects.get(pk=pk)
        except Issue.DoesNotExist:
            raise NotFound(f'Задачу з id={pk} не знайдено.')

    @extend_schema(summary='Задача за id', responses={200: IssueSerializer, 404: NOT_FOUND})
    def get(self, request, pk):
        issue = self.get_object(pk)
        serializer = IssueSerializer(issue)
        return Response(serializer.data)

    @extend_schema(
        summary='Змінити задачу',
        description='Часткове оновлення. Потрібен access токен.',
        examples=[OpenApiExample('Закрити задачу', value={'status': 'closed'}, request_only=True)],
        responses={200: IssueSerializer, 400: INVALID, 401: NO_TOKEN, 404: NOT_FOUND},
    )
    def patch(self, request, pk):
        return save(IssueSerializer(self.get_object(pk), data=request.data, partial=True), request)

    @extend_schema(
        summary='Видалити задачу',
        description='Тільки для адміністратора (is_staff).',
        responses={204: None, 401: NO_TOKEN, 403: error('Користувач не адміністратор'), 404: NOT_FOUND},
    )
    def delete(self, request, pk):
        return destroy(self.get_object(pk), request)
