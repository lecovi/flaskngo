# Standard Lib imports
import json
# Third-party imports
from flask import url_for
# BITSON imports
from tests.test_api import APITestCaseBase
from app.extensions import db
from app.auth.models import RoleGroup, Role


class RolesTestCase(APITestCaseBase):
    def test_get_roles(self):
        self.login()
        url = url_for('auth.get_roles', _external=True)
        response = self.client.get(url, content_type=self.JSON,
                                   headers=self.set_api_headers(
                                       token=self.auth_token),
                                   )
        response.json = self.get_json_response(response)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.json['data'])

    def test_get_role_invalid_id(self):
        self.login()
        invalid_id = RoleGroup.get_invalid_id()
        url = url_for('auth.get_role', item_id=invalid_id,
                      _external=True)
        response = self.client.get(url, content_type=self.JSON,
                                   headers=self.set_api_headers(
                                       token=self.auth_token),
                                   )
        response.json = self.get_json_response(response)
        self.assertEqual(response.status_code, 404)
        self.assertTrue(response.json['data'] == 'item not found')

    def test_get_role(self):
        self.login()
        item_id = Role.get_max_id()
        url = url_for('auth.get_role', item_id=item_id,
                      _external=True)
        response = self.client.get(url, content_type=self.JSON,
                                   headers=self.set_api_headers(
                                       token=self.auth_token),
                                   )
        response.json = self.get_json_response(response)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json['url'] == url)
        self.assertIsNotNone(response.json['data'])

    def test_new_role_not_name(self):
        self.login()
        url = url_for('auth.new_role', _external=True)
        data = {
            'description': 'Test Role',
            'role_group_id': RoleGroup.get_max_id(),
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

    def test_new_role_not_description(self):
        self.login()
        url = url_for('auth.new_role', _external=True)
        data = {
            'name': 'test_role',
            'role_group_id': RoleGroup.get_max_id(),
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

    def test_new_role_not_role_group(self):
        self.login()
        url = url_for('auth.new_role', _external=True)
        data = {
            'name': 'test_role',
            'description': 'Test Role',
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

    def test_new_role_existing_role(self):
        max_role_id = Role.get_max_id()
        self.login()
        url = url_for('auth.new_role', _external=True)
        data = {
            'name': Role.get_by(id=Role.get_max_id()).name,
            'description': 'Duplicate Role',
            'role_group_id': RoleGroup.get_max_id(),
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
        Role.set_sequence_value(value=max_role_id)

    def test_new_role_role_group_id(self):
        self.login()
        url = url_for('auth.new_role', _external=True)
        data = {
            'name': 'test_role',
            'description': 'Test Role',
            'role_group_id': RoleGroup.get_max_id(),
        }
        response = self.client.post(url, content_type=self.JSON,
                                    headers=self.set_api_headers(
                                        token=self.auth_token
                                    ),
                                    data=json.dumps(data),
                                    )
        response.json = self.get_json_response(response)
        new_item = Role.get_by(name=data['name'])
        item_url = url_for('auth.get_role', item_id=new_item.id,
                           _external=True)
        Role.set_sequence_value(value=new_item.id - 1)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.json['data']['url'] == item_url)
        db.session.delete(new_item)
        db.session.commit()

    def test_new_role_role_group_name(self):
        self.login()
        url = url_for('auth.new_role', _external=True)
        data = {
            'name': 'test_role',
            'description': 'Test Role',
            'role_group_name': RoleGroup.get_by(id=RoleGroup.get_max_id()).name,
        }
        response = self.client.post(url, content_type=self.JSON,
                                    headers=self.set_api_headers(
                                        token=self.auth_token
                                    ),
                                    data=json.dumps(data),
                                    )
        response.json = self.get_json_response(response)
        new_item = Role.get_by(name=data['name'])
        item_url = url_for('auth.get_role', item_id=new_item.id,
                           _external=True)
        Role.set_sequence_value(value=new_item.id - 1)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.json['data']['url'] == item_url)
        db.session.delete(new_item)
        db.session.commit()

    def test_new_role(self):
        role_id = Role.get_max_id()
        self.login()
        url = url_for('auth.new_role', _external=True)
        data = {
            'name': 'test_role',
            'description': 'Test Role',
            'role_group_id': 1,
            'role_group_name': RoleGroup.get_by(id=RoleGroup.get_max_id()).name,
        }
        response = self.client.post(url, content_type=self.JSON,
                                    headers=self.set_api_headers(
                                        token=self.auth_token
                                    ),
                                    data=json.dumps(data),
                                    )
        response.json = self.get_json_response(response)
        new_item = Role.get_by(name=data['name'])
        item_url = url_for('auth.get_role', item_id=new_item.id,
                           _external=True)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.json['data']['url'] == item_url)
        self.assertEqual(new_item.role_group.id, 1)
        Role.set_sequence_value(value=role_id)
        db.session.delete(new_item)
        db.session.commit()

    def test_edit_role_no_data(self):
        self.login()
        role = Role.get_by(name='root')
        url = url_for('auth.edit_role', item_id=role.id,
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

    def test_edit_role_invalid_role_group_id(self):
        self.login()
        role = Role.get_by(name='root')
        url = url_for('auth.edit_role', item_id=role.id,
                      _external=True)
        data = {
            'name': "".join([role.name, '_edited']),
            'description': "".join([role.description, '_edited']),
            'role_group_id': RoleGroup.get_invalid_id(),
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

    def test_edit_role_invalid_role_group_name(self):
        self.login()
        role = Role.get_by(name='root')
        url = url_for('auth.edit_role', item_id=role.id,
                      _external=True)
        data = {
            'name': "".join([role.name, '_edited']),
            'description': "".join([role.description, '_edited']),
            'role_group_name': 'invalid_role_group_name',
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

    def test_edit_role_invalid_id(self):
        self.login()
        invalid_id = Role.get_invalid_id()
        url = url_for('auth.edit_role', item_id=invalid_id,
                      _external=True)
        data = {
            'name': 'role_to_edit',
            'description': 'Edited Role',
            'role_group_id': 1,
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

    def test_edit_role_exiting_role(self):
        self.login()
        role = Role.get_by(name='root')
        other_role = Role.get_by(name='user')
        url = url_for('auth.edit_role', item_id=role.id,
                      _external=True)
        data = {
            'name': other_role.name,
            'description': "".join([role.description, '_edited']),
            'role_group_id': role.role_group_id + 1,
            'role_group_name': role.role_group.name,
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

    def test_edit_role(self):
        self.login()
        role = Role.get_by(id=1)
        url = url_for('auth.edit_role', item_id=role.id,
                      _external=True)
        data = {
            'name': "".join([role.name, '_edited']),
            'description': "".join([role.description, '_edited']),
            'role_group_id': role.role_group_id + 1,
            'role_group_name': role.role_group.name,
        }
        response = self.client.put(url, content_type=self.JSON,
                                   headers=self.set_api_headers(
                                       token=self.auth_token
                                   ),
                                   data=json.dumps(data),
                                   )
        response.json = self.get_json_response(response)
        self.assertEqual(response.status_code, 200)
        item_url = url_for('auth.get_role', item_id=role.id, _external=True)
        self.assertTrue(response.json['data']['url'] == item_url)
        role.name, _ = role.name.split('_')
        role.description, _ = role.description.split('_')
        role.role_group_id -= 1
        db.session.commit()

    def test_delete_role_invalid_id(self):
        self.login()
        invalid_id = RoleGroup.get_invalid_id()
        url = url_for('auth.delete_role', item_id=invalid_id,
                      _external=True)
        response = self.client.delete(url, content_type=self.JSON,
                                      headers=self.set_api_headers(
                                          token=self.auth_token
                                      ),
                                      )
        response.json = self.get_json_response(response)
        self.assertEqual(response.status_code, 404)
        self.assertTrue(response.json['error'] == 'not found')

    def test_delete_role(self):
        self.login()
        role = Role.get_by(name='user')
        url = url_for('auth.delete_role', item_id=role.id,
                      _external=True)
        response = self.client.delete(url, content_type=self.JSON,
                                      headers=self.set_api_headers(
                                          token=self.auth_token
                                      ),
                                      )
        self.assertEqual(response.status_code, 204)
        role.set_not_erased()
