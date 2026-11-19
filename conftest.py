import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from catalog.models import Issue, Language, Maintainer, Organization, Project


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user('olena', 'olena@example.com', 'Kv1tka-na-vikni')


@pytest.fixture
def admin(db):
    return User.objects.create_user('admin', 'admin@example.com', 'Kv1tka-na-vikni', is_staff=True)


@pytest.fixture
def user_client(client, user):
    client.force_authenticate(user)
    return client


@pytest.fixture
def admin_client(client, admin):
    client.force_authenticate(admin)
    return client


@pytest.fixture
def project(db):
    project = Project.objects.create(
        name='Test project',
        repo_url='https://github.com/test/test-project',
        difficulty='beginner',
        maintainer=Maintainer.objects.create(full_name='Test Maintainer', github_username='test-maintainer'),
        organization=Organization.objects.create(name='Test org', github_url='https://github.com/test'),
    )
    project.languages.add(Language.objects.create(name='TestLang'))
    return project


@pytest.fixture
def issue(project):
    return Issue.objects.create(project=project, title='Fix typo', difficulty='beginner')
