# Standard Lib imports
# Third-party imports
from flask import url_for
# BITSON imports
from tests.test_api import APITestCaseBase


class LoginTestCase(APITestCaseBase):
    def test_login(self):
        url = url_for('auth.login', _external=True)
        response = self.client.get(url, content_type=self.JSON,
                                   headers=self.set_api_headers(),
                                   )
        response.json = self.get_json_response(response)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json['data']['url'] == url)
        self.assertIsNotNone(response.json['data']['message'])

    def test_login_username(self):
        response = self.login(username_or_email='bitson', password='bitson')
        self.assertEqual(response.status_code, 200)
        self.token = response.json['data']['token']
        self.assertIsNotNone(response.json['data']['token'])
        self.assertTrue(
            response.json['data']['expiration'] == self.app.config.get(
                'SESSION_TTL')
        )

    def test_login_email(self):
        response = self.login(username_or_email='info@bitson.com.ar',
                              password='bitson')
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.json['data']['token'])
        self.assertTrue(
            response.json['data']['expiration'] == self.app.config.get(
                'SESSION_TTL')
        )

    def test_login_bad_username(self):
        response = self.login(username_or_email='bad_username',
                              password='bitson')
        self.assertEqual(response.status_code, 401)
        self.assertTrue(response.json['error'] == 'unauthorized')

    def test_login_bad_email(self):
        response = self.login(username_or_email='bad_email@bitson.com.ar',
                              password='bitson')
        self.assertEqual(response.status_code, 401)
        self.assertTrue(response.json['error'] == 'unauthorized')

    def test_login_bad_password(self):
        response = self.login(username_or_email='bitson',
                              password='bad_password')
        self.assertEqual(response.status_code, 401)
        self.assertTrue(response.json['error'] == 'unauthorized')

    def test_secret(self):
        response = self.login(username_or_email='bitson', password='bitson')
        self.token = response.json['data']['token']

        url = url_for('auth.test_view', _external=True)
        response = self.client.get(url, content_type=self.JSON,
                                   headers=self.set_api_headers(
                                       token=self.token)
                                   )
        self.assertEqual(response.status_code, 200)
        json_response = self.get_json_response(response)
        self.assertIsNotNone(json_response['data']['message'])

    def test_get_token(self):
        response = self.login(username_or_email='bitson', password='bitson')
        self.token = response.json['data']['token']

        url = url_for('auth.get_token', _external=True)

        response = self.client.get(url, content_type=self.JSON,
                                   headers=self.set_api_headers(
                                       token=self.token),
                                   )
        response.json = self.get_json_response(response)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.json['data']['token'])
        self.assertIsNotNone(response.json['data']['expiration'])
