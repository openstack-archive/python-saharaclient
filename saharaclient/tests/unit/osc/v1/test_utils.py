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

from openstackclient.common import exceptions

from saharaclient.osc.v1 import utils
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

    def test_get_resource_id(self):
        class TestResource(object):
            def __init__(self, id):
                self.id = id

        class TestManager(object):

            resource_class = TestResource

            def get(self, id):
                if id == 'id':
                    return TestResource('from_id')
                else:
                    raise

            def find(self, name):
                if name == 'name':
                    return [TestResource('from_name')]
                if name == 'null':
                    return []
                if name == 'mult':
                    return [TestResource('1'), TestResource('2')]

        # check case when resource id is passed
        self.assertEqual('from_id', utils.get_resource(
            TestManager(), 'id').id)

        # check case when resource name is passed
        self.assertEqual('from_name', utils.get_resource(
            TestManager(), 'name').id)

        # check that error is raised when resource doesn't exists
        self.assertRaises(exceptions.CommandError, utils.get_resource,
                          TestManager(), 'null')

        # check that error is raised when multiple resources choice
        self.assertRaises(exceptions.CommandError, utils.get_resource,
                          TestManager(), 'mult')
