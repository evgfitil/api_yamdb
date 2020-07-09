import pytest

from .common import create_users_api, auth_client, create_genre, create_categories, create_titles


class Test04TitleAPI:

    @pytest.mark.django_db(transaction=True)
    def test_01_title_not_auth(self, client):
        response = client.get('/api/v1/titles/')
        assert response.status_code != 404, \
            'The page `/api/v1/titles/` is not found, check it in *urls.py*'
        assert response.status_code == 200, \
            'Check that the GET request `/api/v1/titles/` without token returns 200'

    @pytest.mark.django_db(transaction=True)
    def test_02_title(self, user_client):
        genres = create_genre(user_client)
        categories = create_categories(user_client)
        data = {}
        response = user_client.post('/api/v1/titles/', data=data)
        assert response.status_code == 400, \
            'Check that the POST request`/api/v1/titles/` with wrong data returns 400'
        data = {'name': 'Turn there', 'year': 2000, 'genre': [genres[0]['slug'], genres[1]['slug']],
                'category': categories[0]['slug'], 'description': 'Cool peak'}
        response = user_client.post('/api/v1/titles/', data=data)
        assert response.status_code == 201, \
            'Check that the POST request`/api/v1/titles/` with a valid data returns 201'
        data = {'name': 'Project', 'year': 2020, 'genre': [genres[2]['slug']], 'category': categories[1]['slug'],
                'description': 'Main drama of the year'}
        response = user_client.post('/api/v1/titles/', data=data)
        assert response.status_code == 201, \
            'Check that the POST request`/api/v1/titles/` with a valid data returns 201'
        assert type(response.json().get('id')) == int, \
            'Check that the POST request`/api/v1/titles/` returns generated object data. ' \
            '`id` value not found or not integer.'
        response = user_client.get('/api/v1/titles/')
        assert response.status_code == 200, \
            'Check that the GET request `/api/v1/titles/` returns 200'
        data = response.json()
        assert 'count' in data, \
            'Check that the GET request `/api/v1/titles/` returns a data with paginations. ' \
            '`count` is not found'
        assert 'next' in data, \
            'Check that the GET request `/api/v1/titles/` returns a data with paginations. ' \
            '`next` is not found'
        assert 'previous' in data, \
            'Check that the GET request `/api/v1/titles/` returns a data with paginations. ' \
            '`previous` is not found'
        assert 'results' in data, \
            'Check that the GET request `/api/v1/titles/` returns a data with paginations. ' \
            '`results` is not found'
        assert data['count'] == 2, \
            'Check that the GET request `/api/v1/titles/` returns a data with paginations. ' \
            '`count` have a wrong value'
        assert type(data['results']) == list, \
            'Check that the GET request `/api/v1/titles/` returns a data with paginations. ' \
            '`results` type should be a list'
        assert len(data['results']) == 2, \
            'Check that the GET request `/api/v1/titles/` returns a data with paginations. ' \
            '`results` have a wrong value'
        if data['results'][0].get('name') == 'Turn there':
            title = data['results'][0]
        elif data['results'][1].get('name') == 'Turn there':
            title = data['results'][1]
        else:
            assert False, \
                'Check that the GET request `/api/v1/titles/` returns a data with paginations. ' \
                '`result` have a wrong value, `name` is not found or not saved by POST request.'
        assert title.get('rating') is None, \
            'Check that the GET request `/api/v1/titles/` returns a data with paginations. ' \
            '`result` have a wrong value, `rating` without reviews should be a `None`'
        assert title.get('category') == categories[0], \
            'Check that the GET request `/api/v1/titles/` returns a data with paginations. ' \
            '`result` have a wrong value, `category` have a wrong value' \
            'or not saved by POST request.'
        assert genres[0] in title.get('genre', []) and genres[1] in title.get('genre', []), \
            'Check that the GET request `/api/v1/titles/` returns a data with paginations. ' \
            '`result` have a wrong value, `genre` have a wrong value' \
            'or not saved by POST request.'
        assert title.get('year') == 2000, \
            'Check that the GET request `/api/v1/titles/` returns a data with paginations. ' \
            '`result` have a wrong value, `year` have a wrong value' \
            'or not saved by POST request.'
        assert title.get('description') == 'Cool peak', \
            'Check that the GET request `/api/v1/titles/` returns a data with paginations. ' \
            '`result` have a wrong value, `description` have a wrong value ' \
            'or not saved by POST request.'
        assert type(title.get('id')) == int, \
            'Check that the GET request `/api/v1/titles/` returns a data with paginations. ' \
            '`result` have a wrong value, `id` value not found or not integer.'
        data = {'name': 'Turn', 'year': 2020, 'genre': [genres[1]['slug']],
                'category': categories[1]['slug'], 'description': 'Cool peak'}
        user_client.post('/api/v1/titles/', data=data)
        response = user_client.get(f'/api/v1/titles/?genre={genres[1]["slug"]}')
        data = response.json()
        assert len(data['results']) == 2, \
            'Check that the GET request `/api/v1/titles/` filter by `genre` parameter `slug` genre'
        response = user_client.get(f'/api/v1/titles/?category={categories[0]["slug"]}')
        data = response.json()
        assert len(data['results']) == 1, \
            'Check that the GET request `/api/v1/titles/` filter by `category` parameter `slug` category'
        response = user_client.get(f'/api/v1/titles/?year=2000')
        data = response.json()
        assert len(data['results']) == 1, \
            'Check that the GET request `/api/v1/titles/` filter by `year` parameter year'
        response = user_client.get(f'/api/v1/titles/?name=Turn')
        data = response.json()
        assert len(data['results']) == 2, \
            'Check that the GET request `/api/v1/titles/` filter by `name` parameter name'

    @pytest.mark.django_db(transaction=True)
    def test_03_titles_detail(self, client, user_client):
        titles, categories, genres = create_titles(user_client)
        response = client.get(f'/api/v1/titles/{titles[0]["id"]}/')
        assert response.status_code != 404, \
            'The page `/api/v1/titles/{title_id}/` is not found, check it in *urls.py*'
        assert response.status_code == 200, \
            'Check that the GET request `/api/v1/titles/{title_id}/` ' \
            'without auth token returns 200'
        data = response.json()
        assert type(data.get('id')) == int, \
            'Check that the GET request `/api/v1/titles/{title_id}/` returns a object data. ' \
            '`id` value is not found or not integer.'
        assert data.get('category') == categories[0], \
            'Check that the GET request `/api/v1/titles/{title_id}/` returns a object data. ' \
            '`category` have a wrong value.'
        assert data.get('name') == titles[0]['name'], \
            'Check that the GET request `/api/v1/titles/{title_id}/` returns a object data. ' \
            '`name` have a wrong value.'
        data = {
            'name': 'New name',
            'category': categories[1]['slug']
        }
        response = user_client.patch(f'/api/v1/titles/{titles[0]["id"]}/', data=data)
        assert response.status_code == 200, \
            'Check that the PATCH request  `/api/v1/titles/{title_id}/` returns 200'
        data = response.json()
        assert data.get('name') == 'New name', \
            'Check that the PATCH request`/api/v1/titles/{title_id}/` returns a object data. ' \
            '`name` value has changed.'
        response = user_client.get(f'/api/v1/titles/{titles[0]["id"]}/')
        assert response.status_code == 200, \
            'Check that the GET request `/api/v1/titles/{title_id}/` ' \
            'without token returns 200'
        data = response.json()
        assert data.get('category') == categories[1], \
            'Check that the PATCH request`/api/v1/titles/{title_id}/` `category` value has changed.'
        assert data.get('name') == 'New name', \
            'Check that the PATCH request`/api/v1/titles/{title_id}/` `name` value has changed.'

        response = user_client.delete(f'/api/v1/titles/{titles[0]["id"]}/')
        assert response.status_code == 204, \
            'Check that the DELETE request`/api/v1/titles/{title_id}/` returns 204'
        response = user_client.get('/api/v1/titles/')
        test_data = response.json()['results']
        assert len(test_data) == len(titles) - 1, \
            'Check that the DELETE request`/api/v1/titles/{title_id}/` delete a object'

    def check_permissions(self, user, user_name, titles, categories, genres):
        client_user = auth_client(user)
        data = {'name': 'Beast', 'year': 1999, 'genre': [genres[2]['slug'], genres[1]['slug']],
                'category': categories[0]['slug'], 'description': 'Boom'}
        response = client_user.post('/api/v1/titles/', data=data)
        assert response.status_code == 403, \
            f'Check that the POST request`/api/v1/titles/` ' \
            f'with {user_name} token returns 403'
        response = client_user.patch(f'/api/v1/titles/{titles[0]["id"]}/', data=data)
        assert response.status_code == 403, \
            f'Check that the PATCH request`/api/v1/titles/{{title_id}}/` ' \
            f'with {user_name} token returns 403'
        response = client_user.delete(f'/api/v1/titles/{titles[0]["id"]}/')
        assert response.status_code == 403, \
            f'Check that the DELETE request`/api/v1/titles/{{title_id}}/` ' \
            f'with {user_name} returns 403'

    @pytest.mark.django_db(transaction=True)
    def test_04_titles_check_permission(self, client, user_client):
        titles, categories, genres = create_titles(user_client)
        data = {'name': 'Beast', 'year': 1999, 'genre': [genres[2]['slug'], genres[1]['slug']],
                'category': categories[0]['slug'], 'description': 'Boom'}
        response = client.post('/api/v1/titles/', data=data)
        assert response.status_code == 401, \
            f'Check that the POST request`/api/v1/titles/` ' \
            f'wihtout auth token returns 401'
        response = client.patch(f'/api/v1/titles/{titles[0]["id"]}/', data=data)
        assert response.status_code == 401, \
            f'Check that the PATCH request`/api/v1/titles/{{title_id}}/` ' \
            f'wihtout auth token returns 401'
        response = client.delete(f'/api/v1/titles/{titles[0]["id"]}/')
        assert response.status_code == 401, \
            f'Check that the DELETE request`/api/v1/titles/{{title_id}}/` ' \
            f'wihtout auth token returns 401'
        user, moderator = create_users_api(user_client)
        self.check_permissions(user, 'user', titles, categories, genres)
        self.check_permissions(moderator, 'moderator', titles, categories, genres)
