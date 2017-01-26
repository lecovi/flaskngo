# Standard Lib imports
import json
# Third-party imports
from flask import url_for
# BITSON imports
from tests.test_api import APITestCaseBase
from app.extensions import db
from app.auth.models import User, UserRole


class ResetPasswordTestCase(APITestCaseBase):
    def test_reset_password_request_no_data(self):
        data = {}
        url = url_for('auth.reset_password_request', _external=True)
        response = self.client.post(url, content_type=self.JSON,
                                    headers=self.set_api_headers(),
                                    data=json.dumps(data)
                                    )
        response.json = self.get_json_response(response)
        self.assertEqual(response.status_code, 400)
        self.assertTrue(response.json['error'] == 'bad request')

    def test_reset_password_request_invalid_email(self):
        data = {
            'email': 'invalid@bitson.com.ar',
        }
        url = url_for('auth.reset_password_request', _external=True)
        response = self.client.post(url, content_type=self.JSON,
                                    headers=self.set_api_headers(),
                                    data=json.dumps(data)
                                    )
        response.json = self.get_json_response(response)
        self.assertEqual(response.status_code, 400)
        self.assertTrue(response.json['error'] == 'bad request')

    def test_reset_password_request_invalid_username(self):
        data = {
            'username': 'invalid_username',
        }
        url = url_for('auth.reset_password_request', _external=True)
        response = self.client.post(url, content_type=self.JSON,
                                    headers=self.set_api_headers(),
                                    data=json.dumps(data)
                                    )
        response.json = self.get_json_response(response)
        self.assertEqual(response.status_code, 400)
        self.assertTrue(response.json['error'] == 'bad request')

    def test_reset_password_request_email(self):
        data = {
            'email': 'info@bitson.com.ar',
        }
        url = url_for('auth.reset_password_request', _external=True)
        response = self.client.post(url, content_type=self.JSON,
                                    headers=self.set_api_headers(),
                                    data=json.dumps(data)
                                    )
        response.json = self.get_json_response(response)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.json['data']['token'])
        self.assertIsNotNone(response.json['data']['expiration'])

    def test_reset_password_request_username(self):
        data = {
            'username': 'bitson',
            'email': 'info@bitson.com.ar',
        }
        url = url_for('auth.reset_password_request', _external=True)
        response = self.client.post(url, content_type=self.JSON,
                                    headers=self.set_api_headers(),
                                    data=json.dumps(data)
                                    )
        response.json = self.get_json_response(response)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.json['data']['token'])
        self.assertIsNotNone(response.json['data']['expiration'])

    def test_reset_password_request(self):
        data = {
            'username': 'bitson',
        }
        url = url_for('auth.reset_password_request', _external=True)
        response = self.client.post(url, content_type=self.JSON,
                                    headers=self.set_api_headers(),
                                    data=json.dumps(data)
                                    )
        response.json = self.get_json_response(response)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.json['data']['token'])
        self.assertIsNotNone(response.json['data']['expiration'])

    def test_reset_password_invalid_token(self):
        invalid_token = 'invalid_token'
        url = url_for('auth.reset_password', token=invalid_token, _external=True)
        response = self.client.get(url, content_type=self.JSON,
                                   headers=self.set_api_headers(),
                                   )
        response.json = self.get_json_response(response)
        self.assertEqual(response.status_code, 400)
        self.assertTrue(response.json['error'] == 'bad request')

    def test_reset_password(self):
        user = User.get_by(id=1)
        token = user.generate_reset_token(3600)
        url = url_for('auth.reset_password', token=token,
                      _external=True)
        response = self.client.get(url, content_type=self.JSON,
                                   headers=self.set_api_headers(),
                                   )
        response.json = self.get_json_response(response)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.json['data']['token'])
        self.assertIsNotNone(response.json['data']['expiration'])
        self.assertTrue(
            response.json['data']['url'] == url_for('auth.change_password',
                                                    _external=True)
        )
        self.assertIsNotNone(response.json['data']['message'])

    def test_change_password_no_password(self):
        self.login()
        headers = self.set_api_headers(token=self.auth_token)
        data = {}
        url = url_for('auth.change_password', _external=True)
        response = self.client.post(url, content_type=self.JSON,
                                    headers=headers,
                                    data=json.dumps(data),
                                    )
        response.json = self.get_json_response(response)
        self.assertEqual(response.status_code, 400)
        self.assertTrue(response.json['error'] == 'bad request')

    def test_change_password(self):
        user = User.get_by(username='bitson')
        self.login(username_or_email=user.email)
        headers = self.set_api_headers(token=self.auth_token)
        data = {
            'new_password': 'nueva_clave'
        }
        url = url_for('auth.change_password', _external=True)
        response = self.client.post(url, content_type=self.JSON,
                                    headers=headers,
                                    data=json.dumps(data),
                                    )
        response.json = self.get_json_response(response)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.json['data']['message'])
        user.password = 'bitson'
        db.session.commit()
