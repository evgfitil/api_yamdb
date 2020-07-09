import pytest

from .common import create_users_api, auth_client, create_genre


class Test03GenreAPI:

    @pytest.mark.django_db(transaction=True)
    def test_01_genre_not_auth(self, client):
        response = client.get('/api/v1/genres/')
        assert response.status_code != 404, \
            'The page `/api/v1/genres/` is not found, check it in *urls.py*'
        assert response.status_code == 200, \
            'Check that the GET request `/api/v1/genres/` without auth token returns 200'

    @pytest.mark.django_db(transaction=True)
    def test_02_genre(self, user_client):
        data = {}
        response = user_client.post('/api/v1/genres/', data=data)
        assert response.status_code == 400, \
            'Check that the POST request `/api/v1/genres/` with wrong data returns 400'
        data = {'name': 'Horror', 'slug': 'horror'}
        response = user_client.post('/api/v1/genres/', data=data)
        assert response.status_code == 201, \
            'Check that the POST request `/api/v1/genres/` with valid data 201'
        data = {'name': 'Thriller', 'slug': 'horror'}
        response = user_client.post('/api/v1/genres/', data=data)
        assert response.status_code == 400, \
            'Check that the POST request `/api/v1/genres/` cannot create 2 categories with the same `slug`'
        data = {'name': 'Comedy', 'slug': 'comedy'}
        response = user_client.post('/api/v1/genres/', data=data)
        assert response.status_code == 201, \
            'Check that the POST request `/api/v1/genres/` with valid data 201'
        response = user_client.get('/api/v1/genres/')
        assert response.status_code == 200, \
            'Check that the GET request `/api/v1/genres/` returns 200'
        data = response.json()
        assert 'count' in data, \
            'Check that the GET request `/api/v1/genres/` returns a data with pagination. ' \
            '`count` is not found'
        assert 'next' in data, \
            'Check that the GET request `/api/v1/genres/` returns a data with pagination. ' \
            '`next` is not found'
        assert 'previous' in data, \
            'Check that the GET request `/api/v1/genres/` returns a data with pagination. ' \
            '`previous` is not found'
        assert 'results' in data, \
            'Check that the GET request `/api/v1/genres/` returns a data with pagination. ' \
            '`results` is not found'
        assert data['count'] == 2, \
            'Check that the GET request `/api/v1/genres/` returns a data with pagination. ' \
            '`count` have a wrong value'
        assert type(data['results']) == list, \
            'Check that the GET request `/api/v1/genres/` returns a data with pagination. ' \
            '`results` type should be a list'
        assert len(data['results']) == 2, \
            'Check that the GET request `/api/v1/genres/` returns a data with pagination. ' \
            '`results` have a wrong value'
        assert {'name': 'Horror', 'slug': 'horror'} in data['results'], \
            'Check that the GET request `/api/v1/genres/` returns a data with pagination. ' \
            '`results` have a wrong value'
        response = user_client.get('/api/v1/genres/?search=Horror')
        data = response.json()
        assert len(data['results']) == 1, \
            'Check that the GET request `/api/v1/genres/` filter by search genre name'

    @pytest.mark.django_db(transaction=True)
    def test_03_genres_delete(self, user_client):
        genres = create_genre(user_client)
        response = user_client.delete(f'/api/v1/genres/{genres[0]["slug"]}/')
        assert response.status_code == 204, \
            'Check that the DELETE request `/api/v1/users/genres/{slug}/` retunrs 204'
        response = user_client.get('/api/v1/genres/')
        test_data = response.json()['results']
        assert len(test_data) == len(genres) - 1, \
            'Check that the DELETE request `/api/v1/users/genres/{slug}/` delete category '
        response = user_client.get(f'/api/v1/genres/{genres[0]["slug"]}/')
        assert response.status_code == 405, \
            'Check that the GET request `/api/v1/users/genres/{slug}/` returns 405'
        response = user_client.patch(f'/api/v1/genres/{genres[0]["slug"]}/')
        assert response.status_code == 405, \
            'Check that the PATCH request `/api/v1/users/genres/{slug}/` returns 405'

    def check_permissions(self, user, user_name, genres):
        client_user = auth_client(user)
        data = {
            'name': 'Action',
            'slug': 'action'
        }
        response = client_user.post('/api/v1/genres/', data=data)
        assert response.status_code == 403, \
            f'Check that the POST request `/api/v1/genres/` ' \
            f'with {user_name} token returns 403'
        response = client_user.delete(f'/api/v1/genres/{genres[0]["slug"]}/')
        assert response.status_code == 403, \
            f'Check that the DELETE request `/api/v1/genres/{{slug}}/` ' \
            f'with {user_name} token returns 403'

    @pytest.mark.django_db(transaction=True)
    def test_04_genres_check_permission(self, client, user_client):
        genres = create_genre(user_client)
        data = {
            'name': 'Action',
            'slug': 'action'
        }
        response = client.post('/api/v1/genres/', data=data)
        assert response.status_code == 401, \
            f'Check that the POST request `/api/v1/genres/` ' \
            f'without auth token returns 401'
        response = client.delete(f'/api/v1/genres/{genres[0]["slug"]}/')
        assert response.status_code == 401, \
            f'Check that the DELETE request `/api/v1/genres/{{slug}}/` ' \
            f'without token returns 401'
        user, moderator = create_users_api(user_client)
        self.check_permissions(user, 'user', genres)
        self.check_permissions(moderator, 'moderator', genres)
