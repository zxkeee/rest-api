from django.contrib.auth.models import User
from rest_framework.test import APITestCase

from catalog.models import Issue, Project

REGISTER_URL = '/api/v1/auth/register/'
LOGIN_URL = '/api/v1/auth/login/'
REFRESH_URL = '/api/v1/auth/token/refresh/'
LOGOUT_URL = '/api/v1/auth/logout/'
ME_URL = '/api/v1/auth/me/'


def registration_data(**overrides):
    data = {
        'username': 'olena',
        'email': 'olena@example.com',
        'password': 'Kv1tka-na-vikni',
        'password_confirm': 'Kv1tka-na-vikni',
    }
    data.update(overrides)
    return data


class RegisterTests(APITestCase):
    def test_register_stores_hashed_password(self):
        response = self.client.post(REGISTER_URL, registration_data(), format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['role'], 'user')
        self.assertNotIn('password', response.data)
        user = User.objects.get(username='olena')
        self.assertNotEqual(user.password, 'Kv1tka-na-vikni')
        self.assertTrue(user.check_password('Kv1tka-na-vikni'))

    def test_required_fields(self):
        response = self.client.post(REGISTER_URL, {}, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(set(response.data['errors']), {'username', 'email', 'password', 'password_confirm'})

    def test_invalid_values(self):
        cases = [
            ({'email': 'not-an-email'}, 'email'),
            ({'password_confirm': 'Kv1tka-na-dachi'}, 'password_confirm'),
            ({'password': 'short1', 'password_confirm': 'short1'}, 'password'),
            ({'password': '12345678', 'password_confirm': '12345678'}, 'password'),
            ({'username': 'a' * 151}, 'username'),
            ({'first_name': 'a' * 151}, 'first_name'),
        ]
        for overrides, field in cases:
            with self.subTest(field=field, overrides=overrides):
                response = self.client.post(REGISTER_URL, registration_data(**overrides), format='json')
                self.assertEqual(response.status_code, 400)
                self.assertIn(field, response.data['errors'])

    def test_duplicate_email(self):
        self.client.post(REGISTER_URL, registration_data(), format='json')
        response = self.client.post(REGISTER_URL, registration_data(username='olena2', email='OLENA@example.com'), format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('email', response.data['errors'])


class TokenTests(APITestCase):
    def setUp(self):
        User.objects.create_user('olena', 'olena@example.com', 'Kv1tka-na-vikni')

    def login(self):
        return self.client.post(LOGIN_URL, {'username': 'olena', 'password': 'Kv1tka-na-vikni'}, format='json').data

    def test_login_and_me(self):
        tokens = self.login()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        response = self.client.get(ME_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['username'], 'olena')

    def test_wrong_password(self):
        response = self.client.post(LOGIN_URL, {'username': 'olena', 'password': 'wrong'}, format='json')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['detail'], 'Неправильний username або пароль.')

    def test_me_without_token(self):
        response = self.client.get(ME_URL)
        self.assertEqual(response.status_code, 401)

    def test_refresh_rotates_and_blacklists_old_token(self):
        tokens = self.login()
        response = self.client.post(REFRESH_URL, {'refresh': tokens['refresh']}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)
        self.assertNotEqual(response.data['refresh'], tokens['refresh'])
        again = self.client.post(REFRESH_URL, {'refresh': tokens['refresh']}, format='json')
        self.assertEqual(again.status_code, 401)

    def test_logout_blacklists_refresh(self):
        tokens = self.login()
        response = self.client.post(LOGOUT_URL, {'refresh': tokens['refresh']}, format='json')
        self.assertEqual(response.status_code, 205)
        response = self.client.post(REFRESH_URL, {'refresh': tokens['refresh']}, format='json')
        self.assertEqual(response.status_code, 401)


class PermissionTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user('olena', 'olena@example.com', 'Kv1tka-na-vikni')
        self.admin = User.objects.create_user('admin', 'admin@example.com', 'Kv1tka-na-vikni', is_staff=True)
        self.project = Project.objects.first()

    def test_anonymous_can_read(self):
        self.assertEqual(self.client.get('/api/v1/projects/').status_code, 200)
        self.assertEqual(self.client.get('/api/v1/issues/').status_code, 200)

    def test_anonymous_cannot_write(self):
        response = self.client.post('/api/v1/languages/', {'name': 'Zig'}, format='json')
        self.assertEqual(response.status_code, 401)
        response = self.client.post('/api/v1/issues/', {}, format='json')
        self.assertEqual(response.status_code, 401)

    def test_user_cannot_change_catalog(self):
        self.client.force_authenticate(self.user)
        response = self.client.post('/api/v1/languages/', {'name': 'Zig'}, format='json')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data['detail'], 'Змінювати ці дані може лише адміністратор.')

    def test_user_can_add_issue_but_not_delete(self):
        self.client.force_authenticate(self.user)
        data = {'project': self.project.id, 'title': 'Add tests', 'difficulty': 'beginner'}
        response = self.client.post('/api/v1/issues/', data, format='json')
        self.assertEqual(response.status_code, 201)
        response = self.client.delete(f'/api/v1/issues/{response.data["id"]}/')
        self.assertEqual(response.status_code, 403)

    def test_admin_can_delete_issue(self):
        issue = Issue.objects.create(project=self.project, title='Old', difficulty='beginner')
        self.client.force_authenticate(self.admin)
        response = self.client.delete(f'/api/v1/issues/{issue.id}/')
        self.assertEqual(response.status_code, 204)
        response = self.client.post('/api/v1/languages/', {'name': 'Zig'}, format='json')
        self.assertEqual(response.status_code, 201)
