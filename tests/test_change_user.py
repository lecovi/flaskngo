# Standard Lib imports
import json
# Third-party imports
from flask import url_for
# BITSON imports
from tests.test_api import APITestCaseBase
from app.extensions import db
from app.auth.models import User


class ChangeUserTestCase(APITestCaseBase):
    def test_new_user(self):
        self.login()
        url = url_for('auth.new_user', _external=True)
        response = self.client.post(url, content_type=self.JSON,
                                    headers=self.set_api_headers(
                                        token=self.auth_token,
                                    ),
                                    )
        response.json = self.get_json_response(response)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.json['data']['url'])
        self.assertIsNotNone(response.json['data']['message'])

    def test_change_my_username_no_username(self):
        self.login()
        url = url_for('auth.change_my_username', _external=True)
        data = {}
        response = self.client.put(url, content_type=self.JSON,
                                   headers=self.set_api_headers(
                                       token=self.auth_token,
                                   ),
                                   data=json.dumps(data),
                                   )
        response.json = self.get_json_response(response)
        self.assertEqual(response.status_code, 400)
        self.assertTrue(response.json['error'] == 'bad request')

    def test_change_my_username_invalid_username(self):
        new_user = self.create_user(name='leito')
        self.login()
        url = url_for('auth.change_my_username', _external=True)
        data = {
            'username': 'leito',
        }
        response = self.client.put(url, content_type=self.JSON,
                                   headers=self.set_api_headers(
                                       token=self.auth_token,
                                   ),
                                   data=json.dumps(data),
                                   )
        response.json = self.get_json_response(response)
        self.assertEqual(response.status_code, 400)
        self.assertTrue(response.json['error'] == 'bad request')
        User.remove_fake(item=new_user)

    def test_change_my_username(self):
        user = User.get_by(username='bitson')
        self.login()
        url = url_for('auth.change_my_username', _external=True)
        data = {
            'username': "".join([user.username, '_edited'])
        }
        response = self.client.put(url, content_type=self.JSON,
                                   headers=self.set_api_headers(
                                       token=self.auth_token,
                                   ),
                                   data=json.dumps(data),
                                   )
        response.json = self.get_json_response(response)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.json['data']['message'])
        user.username, _ = user.username.split('_')
        db.session.commit()

    def test_change_username_no_username(self):
        user = self.create_user(name='leito')
        self.login()
        url = url_for('auth.change_username', item_id=user.id, _external=True)
        data = {}
        response = self.client.put(url, content_type=self.JSON,
                                   headers=self.set_api_headers(
                                       token=self.auth_token,
                                   ),
                                   data=json.dumps(data),
                                   )
        response.json = self.get_json_response(response)
        self.assertEqual(response.status_code, 400)
        self.assertTrue(response.json['error'] == 'bad request')
        User.remove_fake(item=user)

    def test_change_username_invalid_username(self):
        user1 = self.create_user(name='leito')
        user2 = self.create_user(name='leo1')
        self.login()
        url = url_for('auth.change_username', item_id=user1.id, _external=True)
        data = {
            'username': user2.username,
        }
        response = self.client.put(url, content_type=self.JSON,
                                   headers=self.set_api_headers(
                                       token=self.auth_token,
                                   ),
                                   data=json.dumps(data),
                                   )
        response.json = self.get_json_response(response)
        self.assertEqual(response.status_code, 400)
        self.assertTrue(response.json['error'] == 'bad request')
        User.remove_fake(item=user2)
        User.remove_fake(item=user1)

    def test_change_username_invalid_id(self):
        invalid_id = User.get_invalid_id()
        self.login()
        url = url_for('auth.change_username', item_id=invalid_id,
                      _external=True)
        data = {
            'username': 'saraza'
        }
        response = self.client.put(url, content_type=self.JSON,
                                   headers=self.set_api_headers(
                                       token=self.auth_token,
                                   ),
                                   data=json.dumps(data),
                                   )
        response.json = self.get_json_response(response)
        self.assertEqual(response.status_code, 404)
        self.assertTrue(response.json['error'] == 'not found')

    def test_change_username(self):
        user = self.create_user(name='leito')
        self.login()
        url = url_for('auth.change_username', item_id=user.id, _external=True)
        data = {
            'username': "".join([user.username, '_edited'])
        }
        response = self.client.put(url, content_type=self.JSON,
                                   headers=self.set_api_headers(
                                       token=self.auth_token,
                                   ),
                                   data=json.dumps(data),
                                   )
        response.json = self.get_json_response(response)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.json['data']['message'])
        User.remove_fake(item=user)

    def test_delete_user_invalid_id(self):
        self.login()
        invalid_id = User.get_invalid_id()
        url = url_for('auth.delete_user', item_id=invalid_id,
                      _external=True)
        response = self.client.delete(url, content_type=self.JSON,
                                      headers=self.set_api_headers(
                                          token=self.auth_token
                                      ),
                                      )
        response.json = self.get_json_response(response)
        self.assertEqual(response.status_code, 404)
        self.assertTrue(response.json['error'] == 'not found')

    def test_delete_user(self):
        self.login()
        user = self.create_user(name='leito')
        url = url_for('auth.delete_user', item_id=user.id,
                      _external=True)
        response = self.client.delete(url, content_type=self.JSON,
                                      headers=self.set_api_headers(
                                          token=self.auth_token
                                      ),
                                      )
        self.assertEqual(response.status_code, 204)
        User.remove_fake(item=user)

    def test_activate_user_invalid_id(self):
        self.login()
        invalid_id = User.get_invalid_id()
        url = url_for('auth.activate_user', item_id=invalid_id,
                      _external=True)
        response = self.client.put(url, content_type=self.JSON,
                                   headers=self.set_api_headers(
                                       token=self.auth_token
                                   ),
                                   )
        response.json = self.get_json_response(response)
        self.assertEqual(response.status_code, 404)
        self.assertTrue(response.json['error'] == 'not found')

    def test_activate_user(self):
        demo_user = self.create_user('leito')
        demo_user.set_inactive()
        self.login()
        # user = User.get_by(username='leito')
        url = url_for('auth.activate_user', item_id=demo_user.id,
                      _external=True)
        response = self.client.put(url, content_type=self.JSON,
                                   headers=self.set_api_headers(
                                       token=self.auth_token
                                   ),
                                   )
        response.json = self.get_json_response(response)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.json['data']['message'])
        User.remove_fake(item=demo_user)

    def test_deactivate_user_invalid_id(self):
        self.login()
        invalid_id = User.get_invalid_id()
        url = url_for('auth.deactivate_user', item_id=invalid_id,
                      _external=True)
        response = self.client.put(url, content_type=self.JSON,
                                   headers=self.set_api_headers(
                                       token=self.auth_token
                                   ),
                                   )
        response.json = self.get_json_response(response)
        self.assertEqual(response.status_code, 404)
        self.assertTrue(response.json['error'] == 'not found')

    def test_deactivate_user(self):
        self.login()
        user = self.create_user(name='leito')
        url = url_for('auth.deactivate_user', item_id=user.id,
                      _external=True)
        response = self.client.put(url, content_type=self.JSON,
                                   headers=self.set_api_headers(
                                       token=self.auth_token
                                   ),
                                   )
        response.json = self.get_json_response(response)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.json['data']['message'])
        User.remove_fake(item=user)
