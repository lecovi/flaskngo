# Standard Lib imports
import json
# Third-party imports
from flask import url_for
# BITSON imports
from tests.test_api import APITestCaseBase
from app.auth.models import User, UserRole


class ConfirmationEmailTestCase(APITestCaseBase):
    def test_confirm_email_invalid_token(self):
        invalid_token = 'invalid_token'
        url = url_for('auth.confirm_email', email_token=invalid_token,
                      _external=True)
        response = self.client.get(url, content_type=self.JSON,
                                   headers=self.set_api_headers(),
                                   )
        response.json = self.get_json_response(response)
        self.assertEqual(response.status_code, 400)
        self.assertTrue(response.json['error'] == 'bad request')

    def test_confirm_email_user_confirmed(self):
        user = User.get_by(id=1)
        user.set_confirmed()
        token = user.generate_email_token(3600)
        url = url_for('auth.confirm_email', email_token=token, _external=True)
        response = self.client.get(url, content_type=self.JSON,
                                   headers=self.set_api_headers(),
                                   )
        response.json = self.get_json_response(response)
        self.assertEqual(response.status_code, 400)
        self.assertTrue(response.json['error'] == 'bad request')

    def test_confirm_email(self):
        user = User.get_by(id=1)
        user.set_not_confirmed()
        token = user.generate_email_token(3600)
        url = url_for('auth.confirm_email', email_token=token, _external=True)
        response = self.client.get(url, content_type=self.JSON,
                                   headers=self.set_api_headers(),
                                   )
        response.json = self.get_json_response(response)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.json['data']['message'])
        user.set_confirmed()

    def test_send_confirmation_email_invalid_email(self):
        user = User.get_by(id=1)
        user.set_confirmed()
        user.set_not_erased()
        user.set_active()
        token = user.generate_auth_token(3600)
        url = url_for('auth.send_confirmation_email', _external=True)
        data = {
            'email': 'invalid@bitson.com.ar'
        }
        response = self.client.post(url, content_type=self.JSON,
                                    headers=self.set_api_headers(token=token),
                                    data=json.dumps(data))
        response.json = self.get_json_response(response)
        self.assertEqual(response.status_code, 400)
        self.assertTrue(response.json['error'] == 'bad request')

    def test_send_confirmation_email_user_confirmed(self):
        user = User.get_by(id=1)
        user.set_confirmed()
        token = user.generate_auth_token(60)
        url = url_for('auth.send_confirmation_email', _external=True)
        data = {
            'email': user.email
        }
        response = self.client.post(url, content_type=self.JSON,
                                    headers=self.set_api_headers(token=token),
                                    data=json.dumps(data))
        response.json = self.get_json_response(response)
        self.assertEqual(response.status_code, 400)
        self.assertTrue(response.json['error'] == 'bad request')

    def test_send_confirmation_email(self):
        user_role_id = UserRole.get_max_id()
        user_to_confirm = self.create_user(name='leito')
        user_to_confirm.set_not_confirmed()
        user = User.get_by(id=1)
        token = user.generate_auth_token(60)
        url = url_for('auth.send_confirmation_email', _external=True)
        data = {
            'email': user_to_confirm.email
        }
        response = self.client.post(url, content_type=self.JSON,
                                    headers=self.set_api_headers(token=token),
                                    data=json.dumps(data))
        response.json = self.get_json_response(response)
        self.assertEqual(response.status_code, 201)
        self.assertIsNotNone(response.json['data']['token'])
        self.assertIsNotNone(response.json['data']['confirm_email_url'])
        self.assertIsNotNone(response.json['data']['expiration'])
        User.remove_fake(user_to_confirm)
        UserRole.set_sequence_value(user_role_id)
