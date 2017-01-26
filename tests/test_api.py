# Standard Lib imports
import json
import unittest
# Third-party imports
from flask import url_for, current_app
# BITSON imports
from app import create_app
from app.extensions import db
from app.auth.models import User


class APITestCaseBase(unittest.TestCase):
    JSON = 'application/json'

    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        self.app_context.pop()

    def login(self, username_or_email='bitson', password='bitson',
              url='auth.login'):
        data = {
            'password': password
        }
        if '@' in username_or_email:
            data.update(dict(email=username_or_email))
        else:
            data.update(dict(username=username_or_email))

        url = url_for(url, _external=True)
        response = self.client.post(url, content_type=self.JSON,
                                    headers=self.set_api_headers(),
                                    data=json.dumps(data))
        response.json = self.get_json_response(response)
        if response.status_code == 200:
            self.auth_token = response.json.get('data').get('token')
        return response

    def set_api_headers(self, token=None, **kwargs):
        self.headers = {
            'Accept': self.JSON,
            'Content-Type': self.JSON
        }
        if token:
            self.headers[self.app.config.get('AUTH_TOKEN_HEADER')] = token
        if kwargs:
            self.headers.update(**kwargs)
        return self.headers

    @staticmethod
    def create_user(name, role='user'):
        return User.create_with_role(username=name, password=name, role=role,
                                     email="{}@demouser.com".format(name))

    @staticmethod
    def get_json_response(response):
        return json.loads(response.data.decode('utf-8'))


class APITestCase(APITestCaseBase):
    def test_app_exists(self):
        self.assertIsNotNone(current_app)

    def test_app_is_testing(self):
        self.assertTrue(current_app.config['TESTING'])

    def test_index(self):
        url = url_for('main.index', _external=True)
        response = self.client.get(url, content_type=self.JSON,
                                   headers=self.set_api_headers(),
                                   )
        response.json = self.get_json_response(response)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json['data']['url'] == url)
        self.assertTrue(
            response.json['data']['login'] == url_for('auth.login',
                                                      _external=True)
        )

if __name__ == '__main__':
    unittest.main()
