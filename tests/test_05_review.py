import pytest

from .common import create_users_api, auth_client, create_titles, create_reviews


class Test05ReviewAPI:

    @pytest.mark.django_db(transaction=True)
    def test_01_review_not_auth(self, client, user_client):
        titles, _, _ = create_titles(user_client)
        response = client.get(f'/api/v1/titles/{titles[0]["id"]}/reviews/')
        assert response.status_code != 404, \
            'The page `/api/v1/titles/{title_id}/reviews/` is not found, check it in *urls.py*'
        assert response.status_code == 200, \
            'Check that the GET request `/api/v1/titles/{title_id}/reviews/` ' \
            'without token returns 200'

    def create_review(self, client_user, title_id, text, score):
        data = {'text': text, 'score': score}
        response = client_user.post(f'/api/v1/titles/{title_id}/reviews/', data=data)
        assert response.status_code == 201, \
            'Check that the POST request `/api/v1/titles/{title_id}/reviews/` ' \
            'with a valid data returns 201, api is available for any authenticated user'
        return response

    @pytest.mark.django_db(transaction=True)
    def test_02_review(self, user_client, admin):
        titles, _, _ = create_titles(user_client)
        user, moderator = create_users_api(user_client)
        client_user = auth_client(user)
        client_moderator = auth_client(moderator)
        data = {}
        response = user_client.post(f'/api/v1/titles/{titles[0]["id"]}/reviews/', data=data)
        assert response.status_code == 400, \
            'Check that the POST request `/api/v1/titles/{title_id}/reviews/` ' \
            'with a wrong data returns 400'
        self.create_review(user_client, titles[0]["id"], 'qwerty', 5)
        self.create_review(client_user, titles[0]["id"], 'qwerty123', 3)
        self.create_review(client_moderator, titles[0]["id"], 'qwerty321', 4)

        self.create_review(user_client, titles[1]["id"], 'qwerty432', 2)
        self.create_review(client_user, titles[1]["id"], 'qwerty534', 4)
        response = self.create_review(client_moderator, titles[1]["id"], 'qwerty231', 3)

        assert type(response.json().get('id')) == int, \
            'Check that the POST request `/api/v1/titles/{title_id}/reviews/` ' \
            'returns the data of the created object. `id` value is not found or not integer.'

        data = {'text': 'kjdfg', 'score': 4}
        response = user_client.post(f'/api/v1/titles/999/reviews/', data=data)
        assert response.status_code == 404, \
            'Check that the POST request `/api/v1/titles/{title_id}/reviews/` ' \
            'with non-existing title_id returns 404.'
        data = {'text': 'аывв', 'score': 11}
        response = user_client.post(f'/api/v1/titles/{titles[0]["id"]}/reviews/', data=data)
        assert response.status_code == 400, \
            'Check that the POST request `/api/v1/titles/{title_id}/reviews/` ' \
            'with `score` greater 10 returns 400.'
        data = {'text': 'sfds', 'score': 0}
        response = user_client.post(f'/api/v1/titles/{titles[0]["id"]}/reviews/', data=data)
        assert response.status_code == 400, \
            'Check that the POST request `/api/v1/titles/{title_id}/reviews/` ' \
            'with `score` less 1 returns 400.'
        data = {'text': 'sfds', 'score': 2}
        response = user_client.post(f'/api/v1/titles/{titles[0]["id"]}/reviews/', data=data)
        assert response.status_code == 400, \
            'Check that the POST request `/api/v1/titles/{title_id}/reviews/` ' \
            'on a previous review for an object returns 400.'

        response = user_client.get(f'/api/v1/titles/{titles[0]["id"]}/reviews/')
        assert response.status_code == 200, \
            'Check that the GET request `/api/v1/titles/{title_id}/reviews/` returns 200'
        data = response.json()
        assert 'count' in data, \
            'Check that the GET request `/api/v1/titles/{title_id}/reviews/` returns a data with pagination. ' \
            '`count` is not found'
        assert 'next' in data, \
            'heck that the GET request `/api/v1/titles/{title_id}/reviews/` returns a data with pagination. ' \
            '`next` is not found'
        assert 'previous' in data, \
            'Check that the GET request `/api/v1/titles/{title_id}/reviews/` returns a data with pagination. ' \
            '`previous` is not found'
        assert 'results' in data, \
            'Check that the GET request `/api/v1/titles/{title_id}/reviews/` returns a data with pagination. ' \
            '`results` is not found'
        assert data['count'] == 3, \
            'Check that the GET request `/api/v1/titles/{title_id}/reviews/` returns a data with pagination. ' \
            '`count` have a wrong value'
        assert type(data['results']) == list, \
            'Check that the GET request `/api/v1/titles/{title_id}/reviews/` returns a data with pagination. ' \
            '`results` type should be a list'
        assert len(data['results']) == 3, \
            'Check that the GET request `/api/v1/titles/{title_id}/reviews/` returns a data with pagination. ' \
            '`results` have a wrong value'

        if data['results'][0].get('text') == 'qwerty':
            review = data['results'][0]
        elif data['results'][1].get('text') == 'qwerty':
            review = data['results'][1]
        elif data['results'][2].get('text') == 'qwerty':
            review = data['results'][2]
        else:
            assert False, \
                'Check that the GET request `/api/v1/titles/{title_id}/reviews/` ' \
                'returns a data with pagination. `results` have a wrong value, ' \
                '`text` is not found or not saved by POST request.'
        assert review.get('score') == 5, \
            'Check that the GET request `/api/v1/titles/{title_id}/reviews/` returns a data with pagination. ' \
            '`results` have a wrong value, `score` is not found or not saved by POST request'
        assert review.get('author') == admin.username, \
            'Check that the GET request `/api/v1/titles/{title_id}/reviews/` returns a data with pagination. ' \
            '`results` have a wrong value, `author` is not found or not saved by POST request.'
        assert review.get('pub_date'), \
            'Check that the GET request `/api/v1/titles/{title_id}/reviews/` returns a data with pagination. ' \
            '`results` have a wrong value, `pub_date` is not found.'
        assert type(review.get('id')) == int, \
            'Check that the GET request `/api/v1/titles/{title_id}/reviews/` returns a data with pagination. ' \
            '`results` have a wrong value, `id` is not found or is not integer.'

        response = user_client.get(f'/api/v1/titles/{titles[0]["id"]}/')
        data = response.json()
        assert data.get('rating') == 4, \
            'Check that the GET request `/api/v1/titles/{title_id}/` ' \
            'with review returns correct `rating` value'
        response = user_client.get(f'/api/v1/titles/{titles[1]["id"]}/')
        data = response.json()
        assert data.get('rating') == 3, \
            'Check that the GET request `/api/v1/titles/{title_id}/` ' \
            'with review returns correct `rating` value'

    @pytest.mark.django_db(transaction=True)
    def test_03_review_detail(self, client, user_client, admin):
        reviews, titles, user, moderator = create_reviews(user_client, admin)
        response = client.get(f'/api/v1/titles/{titles[0]["id"]}/reviews/{reviews[0]["id"]}/')
        assert response.status_code != 404, \
            'The page `/api/v1/titles/{title_id}/reviews/{review_id}/` is not found, check it in *urls.py*'
        assert response.status_code == 200, \
            'Check that the GET request `/api/v1/titles/{title_id}/reviews/{review_id}/` ' \
            'without token returns 200'
        data = response.json()
        assert type(data.get('id')) == int, \
            'Check that the GET request `/api/v1/titles/{title_id}/reviews/{review_id}/` ' \
            'returns a object data. `id` is not found or not integer.'
        assert data.get('score') == reviews[0]['score'], \
            'Check that the GET request `/api/v1/titles/{title_id}/reviews/{review_id}/` ' \
            'returns a object data. `score` have a wrong value.'
        assert data.get('text') == reviews[0]['text'], \
            'Check that the GET request `/api/v1/titles/{title_id}/reviews/{review_id}/` ' \
            'returns a object data. `text` have a wrong value.'
        assert data.get('author') == reviews[0]['author'], \
            'Check that the GET request `/api/v1/titles/{title_id}/reviews/{review_id}/` ' \
            'returns a object data. `author` have a wrong value.'

        data = {
            'text': 'rewq',
            'score': 10
        }
        response = user_client.patch(f'/api/v1/titles/{titles[0]["id"]}/reviews/{reviews[0]["id"]}/', data=data)
        assert response.status_code == 200, \
            'Check that the PATCH request `/api/v1/titles/{title_id}/reviews/{review_id}/` ' \
            'returns 200'
        data = response.json()
        assert data.get('text') == 'rewq', \
            'Check that the PATCH request `/api/v1/titles/{title_id}/reviews/{review_id}/` ' \
            'returns a object data. `text` value has changed.'
        response = user_client.get(f'/api/v1/titles/{titles[0]["id"]}/reviews/{reviews[0]["id"]}/')
        assert response.status_code == 200, \
            'Check that the GET request `/api/v1/titles/{title_id}/reviews/{review_id}/` ' \
            'without token returns 200'
        data = response.json()
        assert data.get('text') == 'rewq', \
            'Check that the PATCH request `/api/v1/titles/{title_id}/reviews/{review_id}/` ' \
            'that the `text` value changes.'
        assert data.get('score') == 10, \
            'Check that the PATCH request `/api/v1/titles/{title_id}/reviews/{review_id}/` ' \
            'that the `score` value changes.'

        client_user = auth_client(user)
        data = {
            'text': 'fgf',
            'score': 1
        }
        response = client_user.patch(f'/api/v1/titles/{titles[0]["id"]}/reviews/{reviews[2]["id"]}/', data=data)
        assert response.status_code == 403, \
            'Check that the PATCH request `/api/v1/titles/{title_id}/reviews/{review_id}/` ' \
            'from user when try to change other people review returns 403'

        data = {
            'text': 'jdfk',
            'score': 7
        }
        response = client_user.patch(f'/api/v1/titles/{titles[0]["id"]}/reviews/{reviews[1]["id"]}/', data=data)
        assert response.status_code == 200, \
            'Check that the PATCH request `/api/v1/titles/{title_id}/reviews/{review_id}/` ' \
            'returns 200'
        data = response.json()
        assert data.get('text') == 'jdfk', \
            'Check that the PATCH request `/api/v1/titles/{title_id}/reviews/{review_id}/` ' \
            'returns a object data. The `text` value has changed.'
        response = user_client.get(f'/api/v1/titles/{titles[0]["id"]}/')
        data = response.json()
        assert data.get('rating') == 7, \
            'Check that the GET request `/api/v1/titles/{title_id}/` ' \
            'with review returns correct `rating` value'

        client_moderator = auth_client(moderator)
        response = client_moderator.delete(f'/api/v1/titles/{titles[0]["id"]}/reviews/{reviews[1]["id"]}/')
        assert response.status_code == 204, \
            'Check that the DELETE request `/api/v1/titles/{title_id}/reviews/{review_id}/` ' \
            'returns 204'
        response = user_client.get(f'/api/v1/titles/{titles[0]["id"]}/reviews/')
        test_data = response.json()['results']
        assert len(test_data) == len(reviews) - 1, \
            'Check that the DELETE request `/api/v1/titles/{title_id}/reviews/{review_id}/` delete a object'

    def check_permissions(self, user, user_name, reviews, titles):
        client_user = auth_client(user)
        data = {'text': 'jdfk', 'score': 7}
        response = client_user.patch(f'/api/v1/titles/{titles[0]["id"]}/reviews/{reviews[0]["id"]}/', data=data)
        assert response.status_code == 403, \
            f'Check that the PATCH request `/api/v1/titles/{{title_id}}/reviews/{{review_id}}/` ' \
            f'with {user_name} token returns 403'
        response = client_user.delete(f'/api/v1/titles/{titles[0]["id"]}/reviews/{reviews[0]["id"]}/')
        assert response.status_code == 403, \
            f'Check that the DELETE request `/api/v1/titles/{{title_id}}/reviews/{{review_id}}/` ' \
            f'with {user_name} token returns 403'

    @pytest.mark.django_db(transaction=True)
    def test_04_reviews_check_permission(self, client, user_client, admin):
        reviews, titles, user, moderator = create_reviews(user_client, admin)
        data = {'text': 'jdfk', 'score': 7}
        response = client.post(f'/api/v1/titles/{titles[0]["id"]}/reviews/', data=data)
        assert response.status_code == 401, \
            f'Check that the POST request `/api/v1/titles/{{title_id}}/reviews/` ' \
            f'without token returns401'
        response = client.patch(f'/api/v1/titles/{titles[0]["id"]}/reviews/{reviews[1]["id"]}/', data=data)
        assert response.status_code == 401, \
            f'Check that the PATCH request `/api/v1/titles/{{title_id}}/reviews/{{review_id}}/` ' \
            f'without token returns401'
        response = client.delete(f'/api/v1/titles/{titles[0]["id"]}/reviews/{reviews[1]["id"]}/')
        assert response.status_code == 401, \
            f'Check that the DELETE request `/api/v1/titles/{{title_id}}/reviews/{{review_id}}/` ' \
            f'without token returns401'
        self.check_permissions(user, 'user', reviews, titles)
