# Copyright (c) 2015 Mirantis Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import mock

from saharaclient.osc import utils
from saharaclient.tests.unit import base


class TestUtils(base.BaseTestCase):
    def test_prepare_data(self):
        data = {'id': '123', 'name_of_res': 'name', 'description': 'descr'}

        fields = ['id', 'name_of_res', 'description']
        expected_data = {'Description': 'descr', 'Id': '123',
                         'Name of res': 'name'}
        self.assertEqual(expected_data, utils.prepare_data(data, fields))

        fields = ['id', 'name_of_res']
        expected_data = {'Id': '123', 'Name of res': 'name'}
        self.assertEqual(expected_data, utils.prepare_data(data, fields))

        fields = ['name_of_res']
        expected_data = {'Name of res': 'name'}
        self.assertEqual(expected_data, utils.prepare_data(data, fields))

    def test_get_resource(self):
        manager = mock.Mock()

        # check case when resource id is passed
        uuid = '82065b4d-2c79-420d-adc3-310de275e922'
        utils.get_resource(manager, uuid)
        manager.get.assert_called_once_with(uuid)

        # check case when resource name is passed
        utils.get_resource(manager, 'name')
        manager.find_unique.assert_called_once_with(name='name')

    def test_get_resource_id(self):
        manager = mock.Mock()

        uuid = '82065b4d-2c79-420d-adc3-310de275e922'
        manager.find_unique.return_value = mock.Mock(id=uuid)

        # check case when resource id is passed
        res = utils.get_resource_id(manager, uuid)
        self.assertEqual(uuid, res)
        manager.get.assert_not_called()
        manager.find_unique.assert_not_called()

        # check case when resource name is passed
        res = utils.get_resource_id(manager, 'name')
        manager.find_unique.assert_called_once_with(name='name')
        self.assertEqual(uuid, res)

    def test_create_dict_from_kwargs(self):
        dict1 = utils.create_dict_from_kwargs(first='1', second=2)
        self.assertEqual({'first': '1', 'second': 2}, dict1)

        dict2 = utils.create_dict_from_kwargs(first='1', second=None)
        self.assertEqual({'first': '1'}, dict2)

        dict3 = utils.create_dict_from_kwargs(first='1', second=False)
        self.assertEqual({'first': '1', 'second': False}, dict3)

    def test_prepare_column_headers(self):
        columns1 = ['first', 'second_column']
        self.assertEqual(
            ['First', 'Second column'], utils.prepare_column_headers(columns1))

        columns2 = ['First', 'Second column']
        self.assertEqual(
            ['First', 'Second column'], utils.prepare_column_headers(columns2))

        columns3 = ['first', 'second_column']
        self.assertEqual(
            ['First', 'Second'], utils.prepare_column_headers(
                columns3, remap={'second_column': 'second'}))
