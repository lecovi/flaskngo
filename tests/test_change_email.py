# Standard Lib imports
import json
# Third-party imports
from flask import url_for
# BITSON imports
from tests.test_api import APITestCaseBase
from app.extensions import db
from app.auth.models import User


class ChangeEmailTestCase(APITestCaseBase):

    def test_change_email_request_invalid_email(self):
        user = User.get_by(id=1)
        token = user.generate_auth_token(3600)
        url = url_for('auth.change_email_request', _external=True)
        data = {
            'new_email': 'info@bitson.com.ar'
        }
        response = self.client.post(url, content_type=self.JSON,
                                    headers=self.set_api_headers(token=token),
                                    data=json.dumps(data))
        response.json = self.get_json_response(response)
        self.assertEqual(response.status_code, 400)
        self.assertTrue(response.json['error'] == 'bad request')

    def test_change_email_request(self):
        user = User.get_by(id=1)
        token = user.generate_auth_token(3600)
        url = url_for('auth.change_email_request', _external=True)
        data = {
            'new_email': 'bitson@bitson.com.ar'
        }
        response = self.client.post(url, content_type=self.JSON,
                                    headers=self.set_api_headers(token=token),
                                    data=json.dumps(data))
        response.json = self.get_json_response(response)
        self.assertEqual(response.status_code, 201)
        self.assertIsNotNone(response.json['data']['token'])
        self.assertIsNotNone(response.json['data']['confirm_email_url'])
        self.assertIsNotNone(response.json['data']['expiration'])
        user.set_confirmed(commit=False)
        user.email = 'info@bitson.com.ar'
        db.session.commit()

    def test_change_email_invalid_token(self):
        invalid_token = 'invalid_token'
        url = url_for('auth.change_email', email_token=invalid_token,
                      _external=True)
        response = self.client.get(url, content_type=self.JSON,
                                   headers=self.set_api_headers(),
                                   )
        response.json = self.get_json_response(response)
        self.assertEqual(response.status_code, 400)
        self.assertTrue(response.json['error'] == 'bad request')

    def test_change_email(self):
        user = User.get_by(id=1)
        user_to_confirm = self.create_user(name='leito')
        user_to_confirm.set_not_confirmed()
        token = user.generate_email_change_token(user_to_confirm.email,
                                                 3600)
        url = url_for('auth.change_email', email_token=token, _external=True)
        response = self.client.get(url, content_type=self.JSON,
                                   headers=self.set_api_headers(),
                                   )
        response.json = self.get_json_response(response)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.json['data']['message'])
        User.remove_fake(item=user_to_confirm)
