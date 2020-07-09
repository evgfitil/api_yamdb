import pytest

from .common import auth_client, create_reviews, create_comments


class Test06CommentAPI:

    @pytest.mark.django_db(transaction=True)
    def test_01_comment_not_auth(self, client, user_client, admin):
        reviews, titles, _, _ = create_reviews(user_client, admin)
        response = client.get(f'/api/v1/titles/{titles[0]["id"]}/reviews/{reviews[0]["id"]}/comments/')
        assert response.status_code != 404, \
            'The page `/api/v1/titles/{title_id}/reviews/{review_id}/comments/` ' \
            'is not found, check it in *urls.py*'
        assert response.status_code == 200, \
            'Check that the GET request `/api/v1/titles/{title_id}/reviews/{review_id}/comments/` ' \
            'without token returns 200'

    def create_comment(self, client_user, title_id, review_id, text):
        data = {'text': text}
        response = client_user.post(f'/api/v1/titles/{title_id}/reviews/{review_id}/comments/', data=data)
        assert response.status_code == 201, \
            'Check that the POST request `/api/v1/titles/{title_id}/reviews/{review_id}/comments/` ' \
            'with a correct data returns 201, api is available for any authenticated user'
        return response

    @pytest.mark.django_db(transaction=True)
    def test_02_comment(self, user_client, admin):
        reviews, titles, user, moderator = create_reviews(user_client, admin)
        client_user = auth_client(user)
        client_moderator = auth_client(moderator)
        data = {}
        response = user_client.post(f'/api/v1/titles/{titles[0]["id"]}/reviews/{reviews[0]["id"]}/comments/', data=data)
        assert response.status_code == 400, \
            'Check that the POST request `/api/v1/titles/{title_id}/reviews/{review_id}/comments/` ' \
            'with a wrong data returns 400'
        self.create_comment(user_client, titles[0]["id"], reviews[0]["id"], 'qwerty')
        self.create_comment(client_user, titles[0]["id"], reviews[0]["id"], 'qwerty123')
        self.create_comment(client_moderator, titles[0]["id"], reviews[0]["id"], 'qwerty321')

        self.create_comment(user_client, titles[0]["id"], reviews[1]["id"], 'qwerty432')
        self.create_comment(client_user, titles[0]["id"], reviews[1]["id"], 'qwerty534')
        response = self.create_comment(client_moderator, titles[0]["id"], reviews[1]["id"], 'qwerty231')

        assert type(response.json().get('id')) == int, \
            'Check that the POST request `/api/v1/titles/{title_id}/reviews/{review_id}/comments/` ' \
            'returns the data of the created object. `id` value is not found or is not integer.'

        data = {'text': 'kjdfg'}
        response = user_client.post(f'/api/v1/titles/999/reviews/999/comments/', data=data)
        assert response.status_code == 404, \
            'Check that the POST request `/api/v1/titles/{title_id}/reviews/{review_id}/comments/` ' \
            'with non-existing title_id or review_id returns 404.'
        data = {'text': 'fssd'}
        response = user_client.post(f'/api/v1/titles/{titles[0]["id"]}/reviews/{reviews[0]["id"]}/comments/', data=data)
        assert response.status_code == 201, \
            'Check that the POST request `/api/v1/titles/{title_id}/reviews/{review_id}/comments/` ' \
            'there is an option to leave few comments for review.'

        response = user_client.get(f'/api/v1/titles/{titles[0]["id"]}/reviews/{reviews[0]["id"]}/comments/')
        assert response.status_code == 200, \
            'Check that the GET request `/api/v1/titles/{title_id}/reviews/{review_id}/comments/` ' \
            'returns 200'
        data = response.json()
        assert 'count' in data, \
            'Check that the GET request `/api/v1/titles/{title_id}/reviews/{review_id}/comments/` ' \
            'returns a data with pagination. `count` is not found.'
        assert 'next' in data, \
            'Check that the GET request `/api/v1/titles/{title_id}/reviews/{review_id}/comments/` ' \
            'returns a data with pagination. `next` is not found.'
        assert 'previous' in data, \
            'Check that the GET request `/api/v1/titles/{title_id}/reviews/{review_id}/comments/` ' \
            'returns a data with pagination. `previous` is not found.'
        assert 'results' in data, \
            'Check that the GET request `/api/v1/titles/{title_id}/reviews/{review_id}/comments/` ' \
            'returns a data with pagination. `results` is not found.'
        assert data['count'] == 4, \
            'Check that the GET request `/api/v1/titles/{title_id}/reviews/{review_id}/comments/` ' \
            'returns a data with pagination. `count` value is wrong'
        assert type(data['results']) == list, \
            'Check that the GET request `/api/v1/titles/{title_id}/reviews/{review_id}/comments/` ' \
            'returns a data with pagination. `results` type should be a list'
        assert len(data['results']) == 4, \
            'Check that the GET request `/api/v1/titles/{title_id}/reviews/{review_id}/comments/` ' \
            'returns a data with pagination. `results` value is wrong'

        comment = None
        for item in data['results']:
            if item.get('text') == 'qwerty':
                comment = item
        assert comment, 'Check that the GET request `/api/v1/titles/{title_id}/reviews/{review_id}/comments/` ' \
                        'returns a data with pagination. `results` value is wrong, ' \
                        '`text` not found or not saved by POST request.'
        assert comment.get('author') == admin.username, \
            'Check that the GET request `/api/v1/titles/{title_id}/reviews/{review_id}/comments/` ' \
            'returns a data with pagination. ' \
            '`results` value is wrong, `author` not found or not saved by POST request.'
        assert comment.get('pub_date'), \
            'Check that the GET request `/api/v1/titles/{title_id}/reviews/{review_id}/comments/`' \
            ' returns a data with pagination. `results` value is wrong, `pub_date` not found.'
        assert type(comment.get('id')) == int, \
            'Check that the GET request `/api/v1/titles/{title_id}/reviews/{review_id}/comments/` ' \
            'returns a data with pagination. ' \
            '`results` value is wrong, `id` value is not found or not integer.'

    @pytest.mark.django_db(transaction=True)
    def test_03_review_detail(self, client, user_client, admin):
        comments, reviews, titles, user, moderator = create_comments(user_client, admin)
        pre_url = f'/api/v1/titles/{titles[0]["id"]}/reviews/{reviews[0]["id"]}/comments/'
        response = client.get(f'{pre_url}{comments[0]["id"]}/')
        assert response.status_code != 404, \
            'The page `/api/v1/titles/{title_id}/reviews/{review_id}/{review_id}/comments/{comment_id}/` ' \
            'is not found, check it in *urls.py*'
        assert response.status_code == 200, \
            'Check that the GET request `/api/v1/titles/{title_id}/reviews/{review_id}/comments/{comment_id}/` ' \
            'without token returns 200'
        data = response.json()
        assert type(data.get('id')) == int, \
            'Check that the GET request `/api/v1/titles/{title_id}/reviews/{review_id}/comments/{comment_id}/` ' \
            'returns the object data. `id` value is not found or is not integer.'
        assert data.get('text') == reviews[0]['text'], \
            'Check that the GET request `/api/v1/titles/{title_id}/reviews/{review_id}/comments/{comment_id}/` ' \
            'returns the object data. `text` value is wrong.'
        assert data.get('author') == reviews[0]['author'], \
            'Check that the GET request `/api/v1/titles/{title_id}/reviews/{review_id}/comments/{comment_id}/` ' \
            'returns the object data. `author` value is wrong.'

        data = {'text': 'rewq'}
        response = user_client.patch(f'{pre_url}{comments[0]["id"]}/', data=data)
        assert response.status_code == 200, \
            'Check that the PATCH request `/api/v1/titles/{title_id}/reviews/{review_id}/comments/{comment_id}/` ' \
            'returns 200'
        data = response.json()
        assert data.get('text') == 'rewq', \
            'Check that the PATCH request `/api/v1/titles/{title_id}/reviews/{review_id}/comments/{comment_id}/` ' \
            'returns the object data. `text` value has changed.'
        response = user_client.get(f'{pre_url}{comments[0]["id"]}/')
        assert response.status_code == 200, \
            'Check that the GET request `/api/v1/titles/{title_id}/reviews/{review_id}/comments/{comment_id}/` ' \
            'without token returns 200'
        data = response.json()
        assert data.get('text') == 'rewq', \
            'Check that the PATCH request `/api/v1/titles/{title_id}/reviews/{review_id}/comments/{comment_id}/` ' \
            'change the `text` value.'

        client_user = auth_client(user)
        data = {'text': 'fgf'}
        response = client_user.patch(f'{pre_url}{comments[2]["id"]}/', data=data)
        assert response.status_code == 403, \
            'Check that the PATCH request `/api/v1/titles/{title_id}/reviews/{review_id}/comments/{comment_id}/` ' \
            'from the user when trying to change the wrong review returns 403'

        data = {'text': 'jdfk'}
        response = client_user.patch(f'{pre_url}{comments[1]["id"]}/', data=data)
        assert response.status_code == 200, \
            'Check that the PATCH request `/api/v1/titles/{title_id}/reviews/{review_id}/comments/{comment_id}/` ' \
            'returns 200'
        data = response.json()
        assert data.get('text') == 'jdfk', \
            'Check that the PATCH request `/api/v1/titles/{title_id}/reviews/{review_id}/comments/{comment_id}/` ' \
            'returns the object data. The `text` value has changed.'

        client_moderator = auth_client(moderator)
        response = client_moderator.delete(f'{pre_url}{comments[1]["id"]}/')
        assert response.status_code == 204, \
            'Check that the DELETE request `/api/v1/titles/{title_id}/reviews/{review_id}/comments/{comment_id}/` ' \
            'returns 204'
        response = user_client.get(f'{pre_url}')
        test_data = response.json()['results']
        assert len(test_data) == len(comments) - 1, \
            'Check that the DELETE request `/api/v1/titles/{title_id}/reviews/{review_id}/comments/{comment_id}/` ' \
            'delete an object'

    def check_permissions(self, user, user_name, pre_url):
        client_user = auth_client(user)
        data = {'text': 'jdfk'}
        response = client_user.patch(pre_url, data=data)
        assert response.status_code == 403, \
            f'Check that the PATCH request `/api/v1/titles/{{title_id}}/reviews/{{review_id}}/` ' \
            f'with {user_name} token returns 403'
        response = client_user.delete(pre_url)
        assert response.status_code == 403, \
            f'Check that the DELETE request `/api/v1/titles/{{title_id}}/reviews/{{review_id}}/` ' \
            f'with {user_name} token returns 403'

    @pytest.mark.django_db(transaction=True)
    def test_04_comment_check_permission(self, client, user_client, admin):
        comments, reviews, titles, user, moderator = create_comments(user_client, admin)
        pre_url = f'/api/v1/titles/{titles[0]["id"]}/reviews/{reviews[0]["id"]}/comments/'
        data = {'text': 'jdfk'}
        response = client.post(f'{pre_url}', data=data)
        assert response.status_code == 401, \
            f'Check that the POST request `/api/v1/titles/{{title_id}}/reviews/{{review_id}}/comments/` ' \
            f'without token returns 401'
        response = client.patch(f'{pre_url}{comments[1]["id"]}/', data=data)
        assert response.status_code == 401, \
            f'Check that the PATCH request `/api/v1/titles/{{title_id}}/reviews/{{review_id}}/comments/{{comment_id}}/` ' \
            f'without token returns 401'
        response = client.delete(f'{pre_url}{comments[1]["id"]}/')
        assert response.status_code == 401, \
            f'Check that the DELETE request `/api/v1/titles/{{title_id}}/reviews/{{review_id}}/comments/{{comment_id}}/` ' \
            f'without token returns 401'
        self.check_permissions(user, 'user', f'{pre_url}{comments[2]["id"]}/')
