import pytest
from django.contrib.auth import get_user_model

from .common import create_users_api, auth_client


class Test01UserAPI:

    @pytest.mark.django_db(transaction=True)
    def test_01_users_not_auth(self, client):
        response = client.get('/api/v1/users/')

        assert response.status_code != 404, \
            'The page `/api/v1/users/` is not found, check it in *urls.py*'

        assert response.status_code == 401, \
            'Check that the GET request `/api/v1/users/` without auth token returns 401'

    @pytest.mark.django_db(transaction=True)
    def test_02_users_username_not_auth(self, client, admin):
        response = client.get(f'/api/v1/users/{admin.username}/')

        assert response.status_code != 404, \
            'The page `/api/v1/users/{username}/` is not found, check it in *urls.py*'

        assert response.status_code == 401, \
            'Check that the GET request `/api/v1/users/{username}/` without auth token returns 401'

    @pytest.mark.django_db(transaction=True)
    def test_03_users_me_not_auth(self, client):
        response = client.get(f'/api/v1/users/me/')

        assert response.status_code != 404, \
            'The page `/api/v1/users/me/` is not found, check it in *urls.py*'

        assert response.status_code == 401, \
            'Check that the GET request `/api/v1/users/me/` without auth token returns 401'

    @pytest.mark.django_db(transaction=True)
    def test_04_users_get_auth(self, user_client, admin):
        response = user_client.get('/api/v1/users/')
        assert response.status_code != 404, \
            'The page `/api/v1/users/` is not found, check it in *urls.py*'
        assert response.status_code == 200, \
            'Check that the GET request `/api/v1/users/` with auth token returns 200'
        data = response.json()
        assert 'count' in data, \
            'Check that the GET request `/api/v1/users/` returns data with pagination. ' \
            '`count` is not found'
        assert 'next' in data, \
            'Check that the GET request `/api/v1/users/` returns data with pagination. ' \
            '`next` is not found'
        assert 'previous' in data, \
            'Check that the GET request `/api/v1/users/` returns data with pagination. ' \
            '`previous` is not found'
        assert 'results' in data, \
            'Check that the GET request `/api/v1/users/` returns data with pagination. ' \
            '`results` is not found'
        assert data['count'] == 1, \
            'Check that the GET request `/api/v1/users/` returns data with pagination. ' \
            'Invalid `count` value'
        assert type(data['results']) == list, \
            'Check that the GET request `/api/v1/users/` returns data with pagination. ' \
            '`results` should be a list'
        assert len(data['results']) == 1 and data['results'][0].get('username') == admin.username \
            and data['results'][0].get('email') == admin.email, \
            'Check that the GET request `/api/v1/users/` returns data with pagination. ' \
            'Invalid `results` value'

    @pytest.mark.django_db(transaction=True)
    def test_05_users_post_auth(self, user_client, admin):
        data = {}
        response = user_client.post('/api/v1/users/', data=data)
        assert response.status_code == 400, \
            'Check that the POST request `/api/v1/users/` with wrong data returns 400'
        data = {
            'username': 'TestUser1231231',
            'role': 'user'
        }
        response = user_client.post('/api/v1/users/', data=data)
        assert response.status_code == 400, \
            'Check that the POST request `/api/v1/users/` with wrong data returns 400'
        data = {
            'username': 'TestUser1231231',
            'role': 'user',
            'email': admin.email
        }
        response = user_client.post('/api/v1/users/', data=data)
        assert response.status_code == 400, \
            'Check that the POST request `/api/v1/users/` with wrong data returns 400. ' \
            '`Email` should be unique'
        data = {
            'username': admin.username,
            'role': 'user',
            'email': 'testuser@yamdb.fake'
        }
        response = user_client.post('/api/v1/users/', data=data)
        assert response.status_code == 400, \
            'Check that the POST request `/api/v1/users/` with wrong data returns 400. ' \
            '`Username` should be unique'
        data = {
            'username': 'TestUser1231231',
            'role': 'user',
            'email': 'testuser@yamdb.fake'
        }
        response = user_client.post('/api/v1/users/', data=data)
        assert response.status_code == 201, \
            'Check that the POST request `/api/v1/users/` with valid data returns 201.'
        data = {
            'first_name': 'fsdfsdf',
            'last_name': 'dsgdsfg',
            'username': 'TestUser4534',
            'bio': 'Jdlkjd',
            'role': 'moderator',
            'email': 'testuser2342@yamdb.fake'
        }
        response = user_client.post('/api/v1/users/', data=data)
        assert response.status_code == 201, \
            'Check that the POST request `/api/v1/users/` with valid data returns 201.'
        response_data = response.json()
        assert response_data.get('first_name') == data['first_name'], \
            'Check that the POST request `/api/v1/users/` with valid data returns `first_name`.'
        assert response_data.get('last_name') == data['last_name'], \
            'Check that the POST request `/api/v1/users/` with valid data returns `last_name`.'
        assert response_data.get('username') == data['username'], \
            'Check that the POST request `/api/v1/users/` with valid data returns `username`.'
        assert response_data.get('bio') == data['bio'], \
            'Check that the POST request `/api/v1/users/` with valid data returns `bio`.'
        assert response_data.get('role') == data['role'], \
            'Check that the POST request `/api/v1/users/` with valid data returns `role`.'
        assert response_data.get('email') == data['email'], \
            'Check that the POST request `/api/v1/users/` with valid data returns `email`.'
        assert get_user_model().objects.count() == 3, \
            'Check that the POST request `/api/v1/users/` create a user.'
        response = user_client.get('/api/v1/users/')
        data = response.json()
        assert len(data['results']) == 3, \
            'Check that the GET request `/api/v1/users/` returns data with pagination. ' \
            'Ivalid `results` value'

    @pytest.mark.django_db(transaction=True)
    def test_06_users_username_get_auth(self, user_client, admin):
        user, moderator = create_users_api(user_client)
        response = user_client.get(f'/api/v1/users/{admin.username}/')
        assert response.status_code != 404, \
            'The page `/api/v1/users/{username}/` is not found, check it in *urls.py*'
        assert response.status_code == 200, \
            'Check that the GET request `/api/v1/users/{username}/` with auth token returns 200'
        response_data = response.json()
        assert response_data.get('username') == admin.username, \
            'Check that the GET request `/api/v1/users/{username}/` returns `username`.'
        assert response_data.get('email') == admin.email, \
            'Check that the GET request `/api/v1/users/{username}/` returns `email`.'

        response = user_client.get(f'/api/v1/users/{moderator.username}/')
        assert response.status_code == 200, \
            'Check that the GET request `/api/v1/users/{username}/` with auth token returns 200'
        response_data = response.json()
        assert response_data.get('username') == moderator.username, \
            'Check that the GET request `/api/v1/users/{username}/` returns `username`.'
        assert response_data.get('email') == moderator.email, \
            'Check that the GET request `/api/v1/users/{username}/` returns `email`.'
        assert response_data.get('first_name') == moderator.first_name, \
            'Check that the GET request `/api/v1/users/` returns `first_name`.'
        assert response_data.get('last_name') == moderator.last_name, \
            'Check that the GET request `/api/v1/users/` returns `last_name`.'
        assert response_data.get('bio') == moderator.bio, \
            'Check that the GET request `/api/v1/users/` returns `bio`.'
        assert response_data.get('role') == moderator.role, \
            'Check that the GET request `/api/v1/users/` returns `role`.'

    @pytest.mark.django_db(transaction=True)
    def test_07_users_username_patch_auth(self, user_client, admin):
        user, moderator = create_users_api(user_client)
        data = {
            'first_name': 'Admin',
            'last_name': 'Test',
            'bio': 'description'
        }
        response = user_client.patch(f'/api/v1/users/{admin.username}/', data=data)
        assert response.status_code == 200, \
            'Check that the PATCH request `/api/v1/users/{username}/` with auth token returns 200'
        test_admin = get_user_model().objects.get(username=admin.username)
        assert test_admin.first_name == data['first_name'], \
            'Check that the PATCH request `/api/v1/users/{username}/` that the data changes.'
        assert test_admin.last_name == data['last_name'], \
            'Check that the PATCH request `/api/v1/users/{username}/` that the data changes.'
        response = user_client.patch(f'/api/v1/users/{user.username}/', data={'role': 'admin'})
        assert response.status_code == 200, \
            'Check that the PATCH request `/api/v1/users/{username}/` with auth token returns 200'
        client_user = auth_client(user)
        response = client_user.get(f'/api/v1/users/{admin.username}/')
        assert response.status_code == 200, \
            'Check that the PATCH request `/api/v1/users/{username}/` user role can be changed'

    @pytest.mark.django_db(transaction=True)
    def test_08_users_username_delete_auth(self, user_client):
        user, moderator = create_users_api(user_client)
        response = user_client.delete(f'/api/v1/users/{user.username}/')
        assert response.status_code == 204, \
            'Check that the DELETE request `/api/v1/users/{username}/` returns 204'
        assert get_user_model().objects.count() == 2, \
            'Check that the DELETE request `/api/v1/users/{username}/` delete a user'

    def check_permissions(self, user, user_name, admin):
        client_user = auth_client(user)
        response = client_user.get('/api/v1/users/')
        assert response.status_code == 403, \
            f'Check that the GET request `/api/v1/users/` ' \
            f'with auth token {user_name} returns 403'
        data = {
            'username': 'TestUser9876',
            'role': 'user',
            'email': 'testuser9876@yamdb.fake'
        }
        response = client_user.post('/api/v1/users/', data=data)
        assert response.status_code == 403, \
            f'Check that the POST request `/api/v1/users/` ' \
            f'with auth token {user_name} returns 403'

        response = client_user.get(f'/api/v1/users/{admin.username}/')
        assert response.status_code == 403, \
            f'Check that the GET request `/api/v1/users/{{username}}/` ' \
            f'with auth token {user_name} returns 403'
        data = {
            'first_name': 'Admin',
            'last_name': 'Test',
            'bio': 'description'
        }
        response = client_user.patch(f'/api/v1/users/{admin.username}/', data=data)
        assert response.status_code == 403, \
            f'Check that the PATCH request `/api/v1/users/{{username}}/` ' \
            f'with auth token {user_name} returns 403'
        response = client_user.delete(f'/api/v1/users/{admin.username}/')
        assert response.status_code == 403, \
            f'Check that the DELETE request `/api/v1/users/{{username}}/` ' \
            f'with auth token {user_name} returns 403'

    @pytest.mark.django_db(transaction=True)
    def test_09_users_check_permissions(self, user_client, admin):
        user, moderator = create_users_api(user_client)
        self.check_permissions(user, 'user', admin)
        self.check_permissions(moderator, 'moderator', admin)

    @pytest.mark.django_db(transaction=True)
    def test_10_users_me_get(self, user_client, admin):
        user, moderator = create_users_api(user_client)
        response = user_client.get(f'/api/v1/users/me/')
        assert response.status_code == 200, \
            'Check that the GET request `/api/v1/users/me/` with auth token returns 200'
        response_data = response.json()
        assert response_data.get('username') == admin.username, \
            'Check that the GET request `/api/v1/users/me/` user data returns'
        client_user = auth_client(moderator)
        response = client_user.get(f'/api/v1/users/me/')
        assert response.status_code == 200, \
            'Check that the GET request `/api/v1/users/me/` with auth token returns 200'
        response_data = response.json()
        assert response_data.get('username') == moderator.username, \
            'Check that the GET request `/api/v1/users/me/` user data returns'
        assert response_data.get('role') == 'moderator', \
            'Check that the GET request `/api/v1/users/me/` user data returns'
        assert response_data.get('email') == moderator.email, \
            'Check that the GET request `/api/v1/users/me/` user data returns'
        response = client_user.delete(f'/api/v1/users/me/')
        assert response.status_code == 405, \
            'Check that the DELETE request `/api/v1/users/me/` returns 405'

    @pytest.mark.django_db(transaction=True)
    def test_11_users_me_patch(self, user_client):
        user, moderator = create_users_api(user_client)
        data = {
            'first_name': 'Admin',
            'last_name': 'Test',
            'bio': 'description'
        }
        response = user_client.patch(f'/api/v1/users/me/', data=data)
        assert response.status_code == 200, \
            'Check that the PATCH request `/api/v1/users/me/` with auth token returns 200'
        response_data = response.json()
        assert response_data.get('bio') == 'description', \
            'Check that the PATCH request `/api/v1/users/me/` changes data'
        client_user = auth_client(moderator)
        response = client_user.patch(f'/api/v1/users/me/', data={'first_name': 'NewTest'})
        test_moderator = get_user_model().objects.get(username=moderator.username)
        assert response.status_code == 200, \
            'Check that the PATCH request `/api/v1/users/me/` with auth token returns 200'
        assert test_moderator.first_name == 'NewTest', \
            'Check that the PATCH request `/api/v1/users/me/` changes data'
