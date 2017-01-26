# Standard Lib imports
import json
# Third-party imports
from flask import url_for
# BITSON imports
from tests.test_api import APITestCaseBase
from app.auth.models import User, UserRole


class RegisterTestCase(APITestCaseBase):
    def test_register_no_username(self):
        response = self.login(username_or_email='bitson', password='bitson')
        self.token = response.json['data']['token']

        url = url_for('auth.register', _external=True)
        data = {
            'email': 'test@bitson.com.ar',
            'password': 'test_user',
            'role': 'normal'
        }
        response = self.client.post(url, content_type=self.JSON,
                                    headers=self.set_api_headers(
                                        token=self.token),
                                    data=json.dumps(data))
        response.json = self.get_json_response(response)
        self.assertEqual(response.status_code, 400)
        self.assertTrue(response.json['error'] == 'bad request')

    def test_register_no_email(self):
        response = self.login(username_or_email='bitson', password='bitson')
        self.token = response.json['data']['token']

        url = url_for('auth.register', _external=True)
        data = {
            'username': 'new_user',
            'password': 'test_user',
            'role': 'normal'
        }
        response = self.client.post(url, content_type=self.JSON,
                                    headers=self.set_api_headers(
                                        token=self.token),
                                    data=json.dumps(data))
        response.json = self.get_json_response(response)
        self.assertEqual(response.status_code, 400)
        self.assertTrue(response.json['error'] == 'bad request')

    def test_register_no_password(self):
        response = self.login(username_or_email='bitson', password='bitson')
        self.token = response.json['data']['token']

        url = url_for('auth.register', _external=True)
        data = {
            'username': 'new_user',
            'email': 'test@bitson.com.ar',
            'role': 'normal'
        }
        response = self.client.post(url, content_type=self.JSON,
                                    headers=self.set_api_headers(
                                        token=self.token),
                                    data=json.dumps(data))
        response.json = self.get_json_response(response)
        self.assertEqual(response.status_code, 400)
        self.assertTrue(response.json['error'] == 'bad request')

    def test_register_no_role(self):
        response = self.login(username_or_email='bitson', password='bitson')
        self.token = response.json['data']['token']

        url = url_for('auth.register', _external=True)
        data = {
            'username': 'new_user',
            'email': 'test@bitson.com.ar',
            'password': 'test_user',
        }
        response = self.client.post(url, content_type=self.JSON,
                                    headers=self.set_api_headers(
                                        token=self.token),
                                    data=json.dumps(data))
        response.json = self.get_json_response(response)
        self.assertEqual(response.status_code, 400)
        self.assertTrue(response.json['error'] == 'bad request')

    def test_register_invalid_username(self):
        response = self.login(username_or_email='bitson', password='bitson')
        self.token = response.json['data']['token']

        url = url_for('auth.register', _external=True)
        data = {
            'username': 'bitson',
            'email': 'test@bitson.com.ar',
            'password': 'test_user',
            'role': 'normal'
        }
        response = self.client.post(url, content_type=self.JSON,
                                    headers=self.set_api_headers(
                                        token=self.token),
                                    data=json.dumps(data))
        response.json = self.get_json_response(response)
        self.assertEqual(response.status_code, 400)
        self.assertTrue(response.json['error'] == 'bad request')

    def test_register_invalid_email(self):
        response = self.login(username_or_email='bitson', password='bitson')
        self.token = response.json['data']['token']

        url = url_for('auth.register', _external=True)
        data = {
            'username': 'new_user',
            'email': 'info@bitson.com.ar',
            'password': 'test_user',
            'role': 'normal'
        }
        response = self.client.post(url, content_type=self.JSON,
                                    headers=self.set_api_headers(
                                        token=self.token),
                                    data=json.dumps(data))
        response.json = self.get_json_response(response)
        self.assertEqual(response.status_code, 400)
        self.assertTrue(response.json['error'] == 'bad request')

    def test_register_invalid_role(self):
        response = self.login(username_or_email='bitson', password='bitson')
        self.token = response.json['data']['token']

        url = url_for('auth.register', _external=True)
        data = {
            'username': 'new_user',
            'email': 'test@bitson.com.ar',
            'password': 'test_user',
            'role': 'invalid_role'
        }
        response = self.client.post(url, content_type=self.JSON,
                                    headers=self.set_api_headers(
                                        token=self.token),
                                    data=json.dumps(data))
        response.json = self.get_json_response(response)
        self.assertEqual(response.status_code, 400)
        self.assertTrue(response.json['error'] == 'bad request')

    def test_register(self):
        response = self.login(username_or_email='bitson', password='bitson')
        user_role_id = UserRole.get_max_id()  # Para no aumentar la secuencia
        #  de las relaciones por demás sin sentido.
        self.token = response.json['data']['token']

        url = url_for('auth.register', _external=True)
        data = {
            'username': 'new_user',
            'email': 'test@bitson.com.ar',
            'password': 'test_user',
            'role': 'user'
        }
        response = self.client.post(url, content_type=self.JSON,
                                    headers=self.set_api_headers(
                                        token=self.token),
                                    data=json.dumps(data))
        response.json = self.get_json_response(response)
        self.assertEqual(response.status_code, 201)
        self.assertIsNotNone(response.json['data']['token'])
        self.assertIsNotNone(response.json['data']['confirm_email_url'])
        self.assertIsNotNone(response.json['data']['expiration'])
        self.assertIsNotNone(User.get_by(username=data['username']))
        user = User.get_by(username=data['username'])
        UserRole.set_sequence_value(value=user_role_id)
        User.remove_fake(item=user)

