import pytest

from catalog.models import Issue

ISSUES = '/api/v1/issues/'


def issue_url(pk):
    return f'{ISSUES}{pk}/'


def test_anonymous_can_list_and_filter(api_client, issue):
    params = {'project': issue.project_id, 'status': 'open', 'difficulty': 'beginner'}
    response = api_client.get(ISSUES, params)
    assert response.status_code == 200
    assert [item['id'] for item in response.data] == [issue.id]


@pytest.mark.parametrize('params', [{'difficulty': 'expert'}, {'status': 'done'}, {'project': 'abc'}, {'project': '²'}])
def test_list_rejects_bad_filters(api_client, db, params):
    response = api_client.get(ISSUES, params)
    assert response.status_code == 400
    assert response.data['status'] == 400


def test_get_issue(api_client, issue):
    response = api_client.get(issue_url(issue.id))
    assert response.status_code == 200
    assert response.data['title'] == 'Fix typo'


def test_get_missing_issue(api_client, db):
    response = api_client.get(issue_url(999999))
    assert response.status_code == 404
    assert response.data['detail'] == 'Задачу з id=999999 не знайдено.'


def test_user_creates_issue(user_client, project):
    data = {'project': project.id, 'title': 'Add tests', 'difficulty': 'beginner'}
    response = user_client.post(ISSUES, data, format='json')
    assert response.status_code == 201
    assert response.data['status'] == 'open'
    assert Issue.objects.filter(id=response.data['id'], project=project).exists()


def test_create_issue_with_invalid_data(user_client, db):
    data = {'project': 999999, 'title': '', 'difficulty': 'expert'}
    response = user_client.post(ISSUES, data, format='json')
    assert response.status_code == 400
    assert set(response.data['errors']) == {'project', 'title', 'difficulty'}


def test_anonymous_cannot_create_issue(api_client, project):
    response = api_client.post(ISSUES, {'project': project.id, 'title': 'X', 'difficulty': 'beginner'}, format='json')
    assert response.status_code == 401


def test_invalid_token(api_client, db):
    api_client.credentials(HTTP_AUTHORIZATION='Bearer broken')
    response = api_client.post(ISSUES, {}, format='json')
    assert response.status_code == 401
    assert response.data['detail'] == 'Токен недійсний або прострочений.'


def test_user_updates_issue(user_client, issue):
    response = user_client.patch(issue_url(issue.id), {'status': 'closed'}, format='json')
    assert response.status_code == 200
    issue.refresh_from_db()
    assert issue.status == 'closed'


def test_update_with_invalid_status(user_client, issue):
    response = user_client.patch(issue_url(issue.id), {'status': 'done'}, format='json')
    assert response.status_code == 400
    assert 'status' in response.data['errors']


def test_anonymous_cannot_update(api_client, issue):
    assert api_client.patch(issue_url(issue.id), {'status': 'closed'}, format='json').status_code == 401


def test_update_missing_issue(user_client, db):
    assert user_client.patch(issue_url(999999), {'status': 'closed'}, format='json').status_code == 404


def test_user_cannot_delete_issue(user_client, issue):
    response = user_client.delete(issue_url(issue.id))
    assert response.status_code == 403
    assert response.data['detail'] == 'Видаляти задачі може лише адміністратор.'
    assert Issue.objects.filter(id=issue.id).exists()


def test_admin_deletes_issue(admin_client, issue):
    assert admin_client.delete(issue_url(issue.id)).status_code == 204
    assert not Issue.objects.filter(id=issue.id).exists()


def test_admin_deletes_missing_issue(admin_client, db):
    assert admin_client.delete(issue_url(999999)).status_code == 404


def test_user_cannot_delete_project(user_client, project):
    assert user_client.delete(f'/api/v1/projects/{project.id}/').status_code == 403


def test_project_with_open_issue_cannot_be_deleted(admin_client, issue):
    response = admin_client.delete(f'/api/v1/projects/{issue.project_id}/')
    assert response.status_code == 409


def test_project_with_closed_issues_can_be_deleted(admin_client, issue):
    issue.status = 'closed'
    issue.save()
    assert admin_client.delete(f'/api/v1/projects/{issue.project_id}/').status_code == 204
    assert not Issue.objects.filter(id=issue.id).exists()


def test_schema_and_docs_are_available(api_client, db):
    assert api_client.get('/api/schema/').status_code == 200
    assert api_client.get('/api/docs/').status_code == 200


def test_login_logs_have_no_secrets(api_client, user, caplog):
    caplog.set_level('INFO')
    login = '/api/v1/auth/login/'
    api_client.post(login, {'username': 'olena', 'password': 'wrong-pass'}, format='json')
    tokens = api_client.post(login, {'username': 'olena', 'password': 'Kv1tka-na-vikni'}, format='json').data
    assert 'Failed login attempt' in caplog.text
    assert f'User id={user.id} logged in' in caplog.text
    for secret in ['wrong-pass', 'Kv1tka-na-vikni', 'olena', tokens['access']]:
        assert secret not in caplog.text
