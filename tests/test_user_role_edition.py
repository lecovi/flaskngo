# Standard Lib imports
# Third-party imports
from flask import url_for
# BITSON imports
from tests.test_api import APITestCaseBase
from app.auth.models import User, Role


class UserRoleEditionTestCase(APITestCaseBase):
    def test_add_role_to_user_invalid_id(self):
        self.login()
        invalid_id = User.get_invalid_id()
        role = Role.get_by(id=1)
        url = url_for('auth.add_role_to_user', item_id=invalid_id,
                      role_name=role.name, _external=True)
        response = self.client.post(url, content_type=self.JSON,
                                    headers=self.set_api_headers(
                                        token=self.auth_token,
                                    ),
                                    )
        response.json = self.get_json_response(response)
        self.assertEqual(response.status_code, 404)
        self.assertTrue(response.json['error'] == 'not found')

    def test_add_role_to_user_already_has_role(self):
        user = self.create_user(name='leito')
        role = user.list_roles_names()[0]
        self.login()
        url = url_for('auth.add_role_to_user', item_id=user.id, role_name=role,
                      _external=True)
        response = self.client.post(url, content_type=self.JSON,
                                    headers=self.set_api_headers(
                                        token=self.auth_token,
                                    ),
                                    )
        response.json = self.get_json_response(response)
        self.assertEqual(response.status_code, 400)
        self.assertTrue(response.json['error'] == 'bad request')
        User.remove_fake(item=user)

    def test_add_role_to_user_invalid_role_name(self):
        user = self.create_user(name='leito')
        role = 'invalid_role'
        self.login()
        url = url_for('auth.add_role_to_user', item_id=user.id, role_name=role,
                      _external=True)
        response = self.client.post(url, content_type=self.JSON,
                                    headers=self.set_api_headers(
                                        token=self.auth_token,
                                    ),
                                    )
        response.json = self.get_json_response(response)
        self.assertEqual(response.status_code, 404)
        self.assertTrue(response.json['error'] == 'not found')
        User.remove_fake(item=user)

    def test_add_role_to_user(self):
        user = self.create_user(name='leito')
        role = Role.create_with_role_group_name(name='test',
                                                description='Test',
                                                role_group_name='user')
        self.login()
        url = url_for('auth.add_role_to_user', item_id=user.id,
                      role_name=role.name, _external=True)
        response = self.client.post(url, content_type=self.JSON,
                                    headers=self.set_api_headers(
                                        token=self.auth_token,
                                    ),
                                    )
        response.json = self.get_json_response(response)
        self.assertEqual(response.status_code, 201)
        self.assertIsNotNone(response.json['data']['message'])
        User.remove_fake(item=user)
        Role.remove_fake(item=role)

    def test_remove_role_from_user_invalid_id(self):
        self.login()
        invalid_id = User.get_invalid_id()
        role = Role.get_by(id=1)
        url = url_for('auth.remove_role_from_user', item_id=invalid_id,
                      role_name=role.name, _external=True)
        response = self.client.post(url, content_type=self.JSON,
                                    headers=self.set_api_headers(
                                        token=self.auth_token,
                                    ),
                                    )
        response.json = self.get_json_response(response)
        self.assertEqual(response.status_code, 404)
        self.assertTrue(response.json['error'] == 'not found')

    def test_remove_role_from_user_doesnt_have_role(self):
        self.login()
        user = self.create_user(name='leito')
        role = Role.create_with_role_group_name(name='test',
                                                description='Test',
                                                role_group_name='user')
        url = url_for('auth.remove_role_from_user', item_id=user.id,
                      role_name=role.name, _external=True)
        response = self.client.delete(url, content_type=self.JSON,
                                      headers=self.set_api_headers(
                                          token=self.auth_token,
                                      ),
                                      )
        response.json = self.get_json_response(response)
        self.assertEqual(response.status_code, 400)
        self.assertTrue(response.json['error'] == 'bad request')
        User.remove_fake(item=user)
        Role.remove_fake(item=role)

    def test_remove_role_from_user_invalid_role_name(self):
        self.login()
        user = self.create_user(name='leito')
        role = 'invalid_role'
        url = url_for('auth.remove_role_from_user', item_id=user.id,
                      role_name=role, _external=True)
        response = self.client.post(url, content_type=self.JSON,
                                    headers=self.set_api_headers(
                                        token=self.auth_token,
                                    ),
                                    )
        response.json = self.get_json_response(response)
        self.assertEqual(response.status_code, 404)
        self.assertTrue(response.json['error'] == 'not found')
        User.remove_fake(item=user)

    def test_remove_role_from_user_with_one_role(self):
        self.login()
        user = self.create_user(name='leito')
        role = user.list_roles_names()[0]
        url = url_for('auth.remove_role_from_user', item_id=user.id,
                      role_name=role, _external=True)
        response = self.client.delete(url, content_type=self.JSON,
                                      headers=self.set_api_headers(
                                          token=self.auth_token,
                                      ),
                                      )
        response.json = self.get_json_response(response)
        self.assertEqual(response.status_code, 400)
        self.assertTrue(response.json['error'] == 'bad request')
        User.remove_fake(item=user)

    def test_remove_role_from_user(self):
        user = self.create_user(name='leito')
        role = Role.create_with_role_group_name(name='test',
                                                description='Test',
                                                role_group_name='user')
        user.add_role(role_name='test')
        self.login()
        url = url_for('auth.remove_role_from_user', item_id=user.id,
                      role_name=role.name, _external=True)
        response = self.client.delete(url, content_type=self.JSON,
                                      headers=self.set_api_headers(
                                          token=self.auth_token,
                                      ),
                                      )
        self.assertEqual(response.status_code, 204)
        User.remove_fake(item=user)
        Role.remove_fake(item=role)
