import pytest

from .common import create_users_api, auth_client, create_categories


class Test02CategoryAPI:

    @pytest.mark.django_db(transaction=True)
    def test_01_category_not_auth(self, client):
        response = client.get('/api/v1/categories/')
        assert response.status_code != 404, \
            'The page `/api/v1/categories/` is not found, check it in *urls.py*'
        assert response.status_code == 200, \
            'Check that the GET request `/api/v1/categories/` without auth token returns 200'

    @pytest.mark.django_db(transaction=True)
    def test_02_category(self, user_client):
        data = {}
        response = user_client.post('/api/v1/categories/', data=data)
        assert response.status_code == 400, \
            'Check that the POST request `/api/v1/categories/` with wrong data returns 400'
        data = {
            'name': 'Movie',
            'slug': 'films'
        }
        response = user_client.post('/api/v1/categories/', data=data)
        assert response.status_code == 201, \
            'Check that the POST request `/api/v1/categories/` with valid data returns 201'
        data = {
            'name': 'New movies',
            'slug': 'films'
        }
        response = user_client.post('/api/v1/categories/', data=data)
        assert response.status_code == 400, \
            'Check that the POST request `/api/v1/categories/` cannot create two categories with the same `slug`'
        data = {
            'name': 'Books',
            'slug': 'books'
        }
        response = user_client.post('/api/v1/categories/', data=data)
        assert response.status_code == 201, \
            'Check that the POST request `/api/v1/categories/` with valid data returns 201'
        response = user_client.get('/api/v1/categories/')
        assert response.status_code == 200, \
            'Check that the GET request `/api/v1/categories/` returns 200'
        data = response.json()
        assert 'count' in data, \
            'Check that the GET request `/api/v1/categories/` returns a data with pagination. ' \
            '`count` is not found'
        assert 'next' in data, \
            'Check that the GET request `/api/v1/categories/` returns a data with pagination. ' \
            '`next` is not found'
        assert 'previous' in data, \
            'Check that the GET request `/api/v1/categories/` returns a data with pagination. ' \
            '`previous` is not found'
        assert 'results' in data, \
            'Check that the GET request `/api/v1/categories/` returns a data with pagination. ' \
            '`results` is not found'
        assert data['count'] == 2, \
            'Check that the GET request `/api/v1/categories/` returns a data with pagination. ' \
            '`count` have a wrong value'
        assert type(data['results']) == list, \
            'Check that the GET request `/api/v1/categories/` returns a data with pagination. ' \
            '`results` type should be a list'
        assert len(data['results']) == 2, \
            'Check that the GET request `/api/v1/categories/` returns a data with pagination. ' \
            '`results` have a wrong value'
        assert {'name': 'Books', 'slug': 'books'} in data['results'], \
            'Check that the GET request `/api/v1/categories/` returns a data with pagination. ' \
            '`results` have a wrong value'
        response = user_client.get('/api/v1/categories/?search=Books')
        data = response.json()
        assert len(data['results']) == 1, \
            'Check that the GET request `/api/v1/categories/` filter by search category name'

    @pytest.mark.django_db(transaction=True)
    def test_03_category_delete(self, user_client):
        create_categories(user_client)
        response = user_client.delete('/api/v1/categories/books/')
        assert response.status_code == 204, \
            'Check that the DELETE request `/api/v1/users/categories/{slug}/` returns 204'
        response = user_client.get('/api/v1/categories/')
        test_data = response.json()['results']
        assert len(test_data) == 1, \
            'Check that the DELETE request `/api/v1/users/categories/{slug}/` delete a category '
        response = user_client.get('/api/v1/categories/books/')
        assert response.status_code == 405, \
            'Check that the GET request `/api/v1/users/categories/{slug}/` returns 405'
        response = user_client.patch('/api/v1/categories/books/')
        assert response.status_code == 405, \
            'Check that the PATCH request `/api/v1/users/categories/{slug}/` returns 405'

    def check_permissions(self, user, user_name, categories):
        client_user = auth_client(user)
        data = {
            'name': 'Music',
            'slug': 'music'
        }
        response = client_user.post('/api/v1/categories/', data=data)
        assert response.status_code == 403, \
            f'Check that the POST request `/api/v1/categories/` ' \
            f'with {user_name} token returns 403'
        response = client_user.delete(f'/api/v1/categories/{categories[0]["slug"]}/')
        assert response.status_code == 403, \
            f'Check that the DELETE request `/api/v1/categories/{{slug}}/` ' \
            f'with {user_name} token returns 403'

    @pytest.mark.django_db(transaction=True)
    def test_04_category_check_permission(self, client, user_client):
        categories = create_categories(user_client)
        data = {
            'name': 'Music',
            'slug': 'music'
        }
        response = client.post('/api/v1/categories/', data=data)
        assert response.status_code == 401, \
            f'Check that the POST request `/api/v1/categories/` ' \
            f'without auth token returns 401'
        response = client.delete(f'/api/v1/categories/{categories[0]["slug"]}/')
        assert response.status_code == 401, \
            f'Check that the DELETE request `/api/v1/categories/{{slug}}/` ' \
            f'without auth token returns 401'
        user, moderator = create_users_api(user_client)
        self.check_permissions(user, 'user', categories)
        self.check_permissions(moderator, 'moderator', categories)
