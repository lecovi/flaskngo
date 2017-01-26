# Standard Lib imports
import json
# Third-party imports
from flask import url_for
# BITSON imports
from tests.test_api import APITestCaseBase
from app.extensions import db
from app.auth.models import RoleGroup


class RoleGroupsTestCase(APITestCaseBase):
    def test_get_role_groups(self):
        self.login()
        url = url_for('auth.get_role_groups', _external=True)
        response = self.client.get(url, content_type=self.JSON,
                                   headers=self.set_api_headers(
                                       token=self.auth_token),
                                   )
        response.json = self.get_json_response(response)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.json['data'])

    def test_get_role_groups_invalid_id(self):
        self.login()
        invalid_id = RoleGroup.get_invalid_id()
        url = url_for('auth.get_role_group', item_id=invalid_id,
                      _external=True)
        response = self.client.get(url, content_type=self.JSON,
                                   headers=self.set_api_headers(
                                       token=self.auth_token),
                                   )
        response.json = self.get_json_response(response)
        self.assertEqual(response.status_code, 404)
        self.assertTrue(response.json['data'] == 'item not found')

    def test_get_role_group(self):
        self.login()
        item_id = RoleGroup.get_max_id()
        url = url_for('auth.get_role_group', item_id=item_id,
                      _external=True)
        response = self.client.get(url, content_type=self.JSON,
                                   headers=self.set_api_headers(
                                       token=self.auth_token),
                                   )
        response.json = self.get_json_response(response)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json['url'] == url)
        self.assertIsNotNone(response.json['data'])

    def test_new_role_groups_not_name(self):
        self.login()
        url = url_for('auth.new_role_group', _external=True)
        data = {
            'description': 'Test Role Group',
        }
        response = self.client.post(url, content_type=self.JSON,
                                    headers=self.set_api_headers(
                                        token=self.auth_token
                                    ),
                                    data=json.dumps(data),
                                    )
        response.json = self.get_json_response(response)
        self.assertEqual(response.status_code, 400)
        self.assertTrue(response.json['error'] == 'bad request')

    def test_new_role_groups_not_description(self):
        self.login()
        url = url_for('auth.new_role_group', _external=True)
        data = {
            'name': 'test_role_group',
        }
        response = self.client.post(url, content_type=self.JSON,
                                    headers=self.set_api_headers(
                                        token=self.auth_token
                                    ),
                                    data=json.dumps(data),
                                    )
        response.json = self.get_json_response(response)
        self.assertEqual(response.status_code, 400)
        self.assertTrue(response.json['error'] == 'bad request')

    def test_new_role_groups_existing_role_groups(self):
        max_id = RoleGroup.get_max_id()
        self.login()
        url = url_for('auth.new_role_group', _external=True)
        data = {
            'name': 'admin',
            'description': 'System Administrators',
        }
        response = self.client.post(url, content_type=self.JSON,
                                    headers=self.set_api_headers(
                                        token=self.auth_token
                                    ),
                                    data=json.dumps(data),
                                    )
        response.json = self.get_json_response(response)
        self.assertEqual(response.status_code, 400)
        self.assertTrue(response.json['error'] == 'bad request')
        RoleGroup.set_sequence_value(value=max_id)

    def test_new_role_groups(self):
        role_group_id = RoleGroup.get_max_id()
        self.login()
        url = url_for('auth.new_role_group', _external=True)
        data = {
            'name': 'test_role_group',
            'description': 'Test Role Group',
        }
        response = self.client.post(url, content_type=self.JSON,
                                    headers=self.set_api_headers(
                                        token=self.auth_token
                                    ),
                                    data=json.dumps(data),
                                    )
        response.json = self.get_json_response(response)
        new_item = RoleGroup.get_by(name=data['name'])
        item_url = url_for('auth.get_role_group', item_id=new_item.id,
                           _external=True)
        RoleGroup.set_sequence_value(value=new_item.id - 1)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.json['data']['url'] == item_url)
        db.session.delete(new_item)
        db.session.commit()
        RoleGroup.set_sequence_value(value=role_group_id)

    def test_edit_role_groups_no_data(self):
        self.login()
        role_group = RoleGroup.get_by(name='admin')
        url = url_for('auth.edit_role_group', item_id=role_group.id,
                      _external=True)
        data = {}
        response = self.client.put(url, content_type=self.JSON,
                                   headers=self.set_api_headers(
                                       token=self.auth_token
                                   ),
                                   data=json.dumps(data),
                                   )
        response.json = self.get_json_response(response)
        self.assertEqual(response.status_code, 400)
        self.assertTrue(response.json['error'] == 'bad request')

    def test_edit_role_groups_invalid_id(self):
        self.login()
        invalid_id = RoleGroup.get_invalid_id()
        url = url_for('auth.edit_role_group', item_id=invalid_id,
                      _external=True)
        data = {
            'name': '_edited',
            'description': '_edited',
        }
        response = self.client.put(url, content_type=self.JSON,
                                   headers=self.set_api_headers(
                                       token=self.auth_token
                                   ),
                                   data=json.dumps(data),
                                   )
        response.json = self.get_json_response(response)
        self.assertEqual(response.status_code, 404)
        self.assertTrue(response.json['error'] == 'not found')

    def test_edit_role_exiting_role_groups(self):
        self.login()
        role_group = RoleGroup.get_by(name='admin')
        another_role_group = RoleGroup.get_by(name='user')
        url = url_for('auth.edit_role_group', item_id=role_group.id,
                      _external=True)
        data = {
            'name': another_role_group.name,
            'description': another_role_group.description,
        }
        response = self.client.put(url, content_type=self.JSON,
                                   headers=self.set_api_headers(
                                       token=self.auth_token
                                   ),
                                   data=json.dumps(data),
                                   )
        response.json = self.get_json_response(response)
        self.assertEqual(response.status_code, 400)
        self.assertTrue(response.json['error'] == 'bad request')

    def test_edit_role_groups(self):
        self.login()
        role_group = RoleGroup.get_by(name='admin')
        url = url_for('auth.edit_role_group', item_id=role_group.id,
                      _external=True)
        data = {
            'name': "".join([role_group.name, '_edited']),
            'description': "".join([role_group.description, '_edited']),
        }
        response = self.client.put(url, content_type=self.JSON,
                                   headers=self.set_api_headers(
                                       token=self.auth_token
                                   ),
                                   data=json.dumps(data),
                                   )
        response.json = self.get_json_response(response)
        self.assertEqual(response.status_code, 200)
        item_url = url_for('auth.get_role_group', item_id=role_group.id,
                           _external=True)
        self.assertTrue(response.json['data']['url'] == item_url)
        role_group.name, _ = role_group.name.split('_')
        role_group.description, _ = role_group.description.split('_')
        db.session.commit()

    def test_delete_role_groups_invalid_id(self):
        self.login()
        invalid_id = RoleGroup.get_invalid_id()
        url = url_for('auth.delete_role_group', item_id=invalid_id,
                      _external=True)
        response = self.client.delete(url, content_type=self.JSON,
                                      headers=self.set_api_headers(
                                          token=self.auth_token
                                      ),
                                      )
        response.json = self.get_json_response(response)
        self.assertEqual(response.status_code, 404)
        self.assertTrue(response.json['error'] == 'not found')

    def test_delete_role_group(self):
        self.login()
        role_group = RoleGroup.get_by(name='user')
        url = url_for('auth.delete_role_group', item_id=role_group.id,
                      _external=True)
        response = self.client.delete(url, content_type=self.JSON,
                                      headers=self.set_api_headers(
                                          token=self.auth_token
                                      ),
                                      )
        self.assertEqual(response.status_code, 204)
        role_group.set_not_erased()
