import logging

from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView

from .errors import error_response, plural
from .models import DIFFICULTY_CHOICES, ISSUE_STATUS_CHOICES, Issue, Language, Maintainer, Organization, Project
from .serializers import IssueSerializer, LanguageSerializer, MaintainerSerializer, OrganizationSerializer, ProjectSerializer

logger = logging.getLogger(__name__)

PROJECT_ORDERING = ['name', '-name', 'stars', '-stars']
DIFFICULTIES = [choice[0] for choice in DIFFICULTY_CHOICES]
ISSUE_STATUSES = [choice[0] for choice in ISSUE_STATUS_CHOICES]


def validation_error(serializer):
    return error_response(status.HTTP_400_BAD_REQUEST, 'Невалідні дані. Деталі в полі errors.', serializer.errors)


def conflict(detail):
    logger.warning(detail)
    return error_response(status.HTTP_409_CONFLICT, detail)


class LanguageList(APIView):
    def get(self, request):
        languages = Language.objects.all()
        serializer = LanguageSerializer(languages, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = LanguageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return validation_error(serializer)


class LanguageDetail(APIView):
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
        language = self.get_object(pk)
        serializer = LanguageSerializer(language, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return validation_error(serializer)

    def delete(self, request, pk):
        language = self.get_object(pk)
        projects_count = language.projects.count()
        if projects_count > 0:
            return conflict(
                f'Неможливо видалити мову «{language.name}», оскільки її використовують '
                f'{plural(projects_count, "проєкт", "проєкти", "проєктів")}. '
                f'Спочатку приберіть цю мову з проєктів.'
            )
        language.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class OrganizationList(APIView):
    def get(self, request):
        organizations = Organization.objects.all()
        search = request.query_params.get('search')
        if search:
            organizations = organizations.filter(name__icontains=search)
        serializer = OrganizationSerializer(organizations, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = OrganizationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return validation_error(serializer)


class OrganizationDetail(APIView):
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
        organization = self.get_object(pk)
        serializer = OrganizationSerializer(organization, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return validation_error(serializer)

    def delete(self, request, pk):
        organization = self.get_object(pk)
        projects_count = organization.projects.count()
        if projects_count > 0:
            return conflict(
                f'Неможливо видалити організацію «{organization.name}», оскільки за нею закріплено '
                f'{plural(projects_count, "проєкт", "проєкти", "проєктів")}. '
                f'Спочатку видаліть ці проєкти або перенесіть їх в іншу організацію.'
            )
        organization.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class OrganizationProjects(APIView):
    def get(self, request, pk):
        try:
            organization = Organization.objects.get(pk=pk)
        except Organization.DoesNotExist:
            raise NotFound(f'Організацію з id={pk} не знайдено.')
        serializer = ProjectSerializer(organization.projects.all(), many=True)
        return Response(serializer.data)


class MaintainerList(APIView):
    def get(self, request):
        maintainers = Maintainer.objects.all()
        search = request.query_params.get('search')
        if search:
            maintainers = maintainers.filter(full_name__icontains=search)
        serializer = MaintainerSerializer(maintainers, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = MaintainerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return validation_error(serializer)


class MaintainerDetail(APIView):
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
        maintainer = self.get_object(pk)
        serializer = MaintainerSerializer(maintainer, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return validation_error(serializer)

    def delete(self, request, pk):
        maintainer = self.get_object(pk)
        projects_count = maintainer.projects.count()
        if projects_count > 0:
            return conflict(
                f'Неможливо видалити мейнтейнера «{maintainer.full_name}», оскільки за ним закріплено '
                f'{plural(projects_count, "проєкт", "проєкти", "проєктів")}. '
                f'Спочатку призначте цим проєктам іншого мейнтейнера.'
            )
        maintainer.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MaintainerProjects(APIView):
    def get(self, request, pk):
        try:
            maintainer = Maintainer.objects.get(pk=pk)
        except Maintainer.DoesNotExist:
            raise NotFound(f'Мейнтейнера з id={pk} не знайдено.')
        serializer = ProjectSerializer(maintainer.projects.all(), many=True)
        return Response(serializer.data)


class ProjectList(APIView):
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
        serializer = ProjectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return validation_error(serializer)


class ProjectDetail(APIView):
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
        project = self.get_object(pk)
        serializer = ProjectSerializer(project, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return validation_error(serializer)

    def delete(self, request, pk):
        project = self.get_object(pk)
        open_issues_count = project.issues.filter(status__in=['open', 'in_progress']).count()
        if open_issues_count > 0:
            return conflict(
                f'Неможливо видалити проєкт «{project.name}», оскільки він має '
                f'{plural(open_issues_count, "незакриту задачу", "незакриті задачі", "незакритих задач")}. '
                f'Спочатку закрийте або видаліть їх.'
            )
        project.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class IssueList(APIView):
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

    def post(self, request):
        serializer = IssueSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return validation_error(serializer)


class IssueDetail(APIView):
    def get_object(self, pk):
        try:
            return Issue.objects.get(pk=pk)
        except Issue.DoesNotExist:
            raise NotFound(f'Задачу з id={pk} не знайдено.')

    def get(self, request, pk):
        issue = self.get_object(pk)
        serializer = IssueSerializer(issue)
        return Response(serializer.data)

    def patch(self, request, pk):
        issue = self.get_object(pk)
        serializer = IssueSerializer(issue, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return validation_error(serializer)

    def delete(self, request, pk):
        issue = self.get_object(pk)
        issue.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
